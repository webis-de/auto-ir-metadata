import sys
import tempfile
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, Optional

import nbformat
from nbconvert import HTMLExporter
from pkg_resources import working_set
from py_measure import Environment as PyMeasureEnvironment

FILE_NAME = ".ir-metadata"


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


def _fail_if_parameters_have_wrong_types(
    system_name: Optional[str], system_description: Optional[str], environment: Optional[str]
):
    if environment is not None and not isinstance(environment, PyMeasureEnvironment):
        raise ValueError("Invalid type of environment, I expected an py_measure.Environment.")

    if system_name and not isinstance(system_name, str):
        raise ValueError("Invalid type of system_name, I expected an string.")

    if system_description and not isinstance(system_description, str):
        raise ValueError("Invalid type of system_description, I expected an string.")


def _executed_file_from_stacktrace() -> Path:
    return Path(traceback.extract_stack()[0].filename).resolve()


def parse_notebook_to_html(notebook_content):
    try:
        notebook = nbformat.reads(notebook_content, as_version=4)
        html_exporter = HTMLExporter(template_name="classic")
        (body, _) = html_exporter.from_notebook_node(notebook)
        return body
    except Exception:
        pass


def get_url_of_git_repo(metadata):
    try:
        url = [i for i in metadata["git"]["remotes"].values()][0]
        url = url.replace(".git", "")
        commit = metadata["git"]["commit"]

        if url.startswith("git@"):
            url = url.replace(":", "/")
            url = url.replace("git@", "https://")
        return f"{url}/tree/{commit}"
    except Exception:
        return None


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
