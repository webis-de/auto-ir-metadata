import json
import zipfile
from pathlib import Path
from typing import Optional

from py_measure import Environment as PyMeasureEnvironment

import auto_ir_metadata.utils as utils


class Environment(PyMeasureEnvironment):
    pass


def persist_ir_metadata(
    output_directory: Path,
    system_name: Optional[str] = None,
    system_description: Optional[str] = None,
    environment: Optional[PyMeasureEnvironment] = None,
):
    if output_directory and isinstance(output_directory, str):
        output_directory = Path(output_directory)

    utils._fail_if_parameters_have_wrong_types(system_name, system_description, environment)
    utils.__ensure_output_directory_is_valid(output_directory)
    output_file = output_directory / utils.FILE_NAME
    collected_meta_data = utils.get_python_info()

    if not environment:
        environment = Environment(["git"])
        environment.start_measuring()
        environment.stop_measuring()

    if len(environment.measurements) > 0:
        for k, v in environment.measurements[-1].items():
            collected_meta_data[k] = v

    if system_name:
        collected_meta_data["system_name"] = system_name

    if system_description:
        collected_meta_data["system_description"] = system_description

    if utils._is_notebook():
        script, notebook = utils._notebook_contents()
        collected_meta_data["file"] = {"name": script.name, "content": open(script, "r").read()}
        collected_meta_data["notebook"] = {"name": notebook.name, "content": open(notebook, "r").read()}
    else:
        executed_file = utils._executed_file_from_stacktrace()
        collected_meta_data["file"] = {"name": executed_file.name, "content": open(executed_file, "r").read()}

    serialized_meta_data = json.dumps(collected_meta_data)

    with open(output_file, "w") as f:
        f.write(serialized_meta_data)


def load_ir_metadata(directory: Path, decompress: bool = False):
    if directory.is_dir() and (directory / ".ir-metadata").is_file():
        return load_ir_metadata(directory / ".ir-metadata")

    if decompress:
        archive = zipfile.ZipFile(directory, "r")
        matches = [i.filename for i in archive.filelist]
        matches = [i for i in matches if i and i.endswith(".ir-metadata")]
        if len(matches) == 1:
            ret = json.loads(archive.read(matches[0]).decode("UTF-8"))
        else:
            raise ValueError(f"Could not load metadata from zip archive. Found: {archive.filelist}.")
    else:
        ret = json.load(open(directory))

    if "notebook" in ret and "content" in ret["notebook"]:
        ret["notebook_html"] = utils.parse_notebook_to_html(json.dumps(json.loads(ret["notebook"]["content"])))
        if not ret["notebook_html"]:
            del ret["notebook_html"]

    if "git" in ret and utils.get_url_of_git_repo(ret):
        ret["git_url"] = utils.get_url_of_git_repo(ret)

    return ret
