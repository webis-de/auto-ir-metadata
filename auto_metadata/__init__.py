import json
import sys
from pathlib import Path

from pkg_resources import working_set

FILE_NAME = ".ir-metadata"


def __ensure_output_directory_is_valid(output_directory: Path):
    if not output_directory:
        raise ValueError("Foo")

    if output_directory.is_file():
        raise ValueError("Foo")

    if (output_directory / FILE_NAME).exists():
        raise ValueError("Foo")

    if not output_directory.is_dir():
        output_directory.mkdirs(parents=True, exist_ok=True)


def collect_meta_data() -> dict:
    ret = {}
    modules = [i.split(".")[0] for i in sys.modules.keys() if i and not i.startswith("_")]
    pkg_resources = list(set([f"{i.project_name}=={i.version}" for i in working_set]))
    ret["sys"] = {
        "executable": sys.executable,
        "argv": sys.argv,
        "modules": list(set(modules)),
        "version_info": sys.version_info,
    }
    ret["pkg_resources"] = pkg_resources
    return ret


def persist_ir_metadata(output_directory: Path):
    __ensure_output_directory_is_valid(output_directory)
    output_file = output_directory / FILE_NAME
    collected_meta_data = collect_meta_data()
    collected_meta_data = json.dumps(collected_meta_data)
    with open(output_file, "w") as f:
        f.write(collected_meta_data)
