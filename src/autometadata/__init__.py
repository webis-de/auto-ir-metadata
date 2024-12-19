import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from git import InvalidGitRepositoryError, Repo
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


def _executed_file_from_stacktrace() -> Path:
    return Path(traceback.extract_stack()[0].filename).resolve()


def collect_git_repo_metadata(repo: Optional[Path] = None) -> Dict[str, Any]:
    if not repo:
        return collect_git_repo_metadata(_executed_file_from_stacktrace().parent)
    git_repo = None
    try:
        git_repo = Repo(repo)
    except InvalidGitRepositoryError:
        parent_repo = repo.parent
        cnt = 0

        while cnt < 7 and parent_repo != Path("/"):
            try:
                cnt += 1
                git_repo = Repo(parent_repo)
                break
            except InvalidGitRepositoryError:
                parent_repo = parent_repo.parent

        if not git_repo:
            raise InvalidGitRepositoryError(f"I can not find a git repository in {repo}.")

    remotes = {r.name: r.url for r in git_repo.remotes}

    return {
        "commit": git_repo.head.commit.hexsha,
        "active_branch": git_repo.active_branch.name,
        "remotes": remotes,
    }


def collect_meta_data() -> Dict[str, Any]:
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


def persist_ir_metadata(output_directory: Path):
    __ensure_output_directory_is_valid(output_directory)
    output_file = output_directory / FILE_NAME
    collected_meta_data = collect_meta_data()
    collected_meta_data["git"] = collect_git_repo_metadata()
    serialized_meta_data = json.dumps(collected_meta_data)
    with open(output_file, "w") as f:
        f.write(serialized_meta_data)
