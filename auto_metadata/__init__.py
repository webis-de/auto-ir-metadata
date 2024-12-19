import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from git import Repo
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
        output_directory.mkdir(parents=True, exist_ok=True)


def collect_git_repo_metadata(repo: Optional[Path] = None) -> Dict[str, Any]:
    if not repo:
        return collect_git_repo_metadata(Path(traceback.extract_stack()[0].filename).parent.resolve())

    git_repo = Repo(repo)
    remotes = {r.name: r.url for r in git_repo.remotes}

    return {
        "commit": git_repo.head.commit.hexsha,
        "active_branch": git_repo.active_branch.name,
        "remotes": remotes,
    }


def collect_meta_data() -> Dict[str, Any]:
    ret : Dict[str, Any] = {}
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


def persist_ir_metadata(output_directory: Path):
    __ensure_output_directory_is_valid(output_directory)
    output_file = output_directory / FILE_NAME
    collected_meta_data = collect_meta_data()
    collected_meta_data["git"] = collect_git_repo_metadata()
    serialized_meta_data = json.dumps(collected_meta_data)
    with open(output_file, "w") as f:
        f.write(serialized_meta_data)
