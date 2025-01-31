import json
import sys
import tempfile
import traceback
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, Optional

import nbformat
from nbconvert import HTMLExporter
from pkg_resources import working_set
from py_measure import Environment as PyMeasureEnvironment

FILE_NAME = ".ir-metadata"


class Environment(PyMeasureEnvironment):
    pass


def __ensure_output_directory_is_valid(outdir: Path):
    if not outdir:
        raise ValueError("Foo")

    if isinstance(outdir, str):
        outdir = Path(outdir)

    if outdir.exists() and not outdir.is_dir():
        raise ValueError("Foo")

    if (outdir / FILE_NAME).exists():
        raise ValueError("Foo")

    if not outdir.is_dir():
        outdir.mkdir(parents=True, exist_ok=True)


def _is_notebook() -> bool:
    try:
        from IPython import get_ipython

        return get_ipython() is not None  # type: ignore
    except ImportError:
        return False


def _notebook_contents() -> tuple[Path, Path]:
    if not _is_notebook():
        raise ValueError("foo")

    from IPython import get_ipython

    ipython = get_ipython()  # type: ignore

    with tempfile.TemporaryDirectory(delete=False) as f:
        python_file = Path(f) / "script.py"
        notebook_file = Path(f) / "notebook.ipynb"
        with redirect_stdout(None):
            ipython.magic(f"save -f {python_file} 1-9999")
            ipython.magic(f"notebook {notebook_file}")

        return python_file, notebook_file


def _executed_file_from_stacktrace() -> Path:
    return Path(traceback.extract_stack()[0].filename).resolve()


def get_python_info() -> Dict[str, Any]:
    ret: Dict[str, Any] = {}
    modules = [i.split(".")[0] for i in sys.modules.keys() if i and not i.startswith("_")]
    pkg_resources = list(set([f"{i.project_name}=={i.version}" for i in working_set]))
    ret["sys"] = {
        "executable": sys.executable,
        "argv": sys.argv,
        "modules": list(set(modules)),
        "version_info": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    ret["pkg_resources"] = pkg_resources
    return ret


def persist_ir_metadata(
        output_directory: Path,
        system_name: Optional[str] = None,
        system_description: Optional[str] = None,
        environment: Optional[str] = None,
        ):
    if output_directory and isinstance(output_directory, str):
        output_directory = Path(output_directory)

    __ensure_output_directory_is_valid(output_directory)
    output_file = output_directory / FILE_NAME
    collected_meta_data = get_python_info()

    if not environment:
        environment = Environment(verbose=True)
        environment.start_measuring()
        environment.stop_measuring()

    if len(environment.measurements) > 0:
        for k, v in environment.measurements[-1].items():
            collected_meta_data[k] = v

    if system_name:
        collected_meta_data['system_name'] = system_name

    if system_description:
        collected_meta_data['system_description'] = system_description

    if _is_notebook():
        script, notebook = _notebook_contents()
        collected_meta_data["file"] = {"name": script.name, "content": open(script, "r").read()}
        collected_meta_data["notebook"] = {"name": notebook.name, "content": open(notebook, "r").read()}
    else:
        executed_file = _executed_file_from_stacktrace()
        collected_meta_data["file"] = {"name": executed_file.name, "content": open(executed_file, "r").read()}

    serialized_meta_data = json.dumps(collected_meta_data)

    with open(output_file, "w") as f:
        f.write(serialized_meta_data)


def get_url_of_git_repo(metadata):
    try:
        url = [i for i in metadata['git']['remotes'].values()][0]
        url = url.replace('.git', '')
        commit = metadata['git']['commit']

        if url.startswith('git@'):
            url = url.replace(':', '/')
            url = url.replace('git@', 'https://')
        return f'{url}/tree/{commit}'
    except:
        return None

def load_ir_metadata(directory: Path, decompress: bool = False):
    if directory.is_dir() and (directory / '.ir-metadata').is_file():
        return load_ir_metadata(directory / '.ir-metadata')

    if decompress:
        archive = zipfile.ZipFile(directory, 'r')
        matches = [i.filename for i in archive.filelist]
        matches = [i for i in matches if i and i.endswith('.ir-metadata')]
        if len(matches) == 1:
            ret = json.loads(archive.read(matches[0]).decode('UTF-8'))
        else:
            raise ValueError(f'Could not load metadata from zip archive. Found: {archive.filelist}.')
    else:
        ret = json.load(open(directory))

    if 'notebook' in ret and 'content' in ret['notebook']:
        try:
            notebook_content = json.dumps(json.loads(ret['notebook']['content']))

            notebook = nbformat.reads(notebook_content, as_version=4)
            html_exporter = HTMLExporter(template_name="classic")
            (body, _) = html_exporter.from_notebook_node(notebook)
            ret['notebook_html'] = body
        except:
            pass
    
    if 'git' in ret and get_url_of_git_repo(ret):
        ret['git_url'] = get_url_of_git_repo(ret)

    return ret
