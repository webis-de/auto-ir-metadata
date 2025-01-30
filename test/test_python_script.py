import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from approvaltests import verify_as_json

ROOT_DIR = Path(__file__).parent.parent.resolve()
TEST_RESOURCES = ROOT_DIR / "test" / "test-resources.zip"


@contextmanager
def resource(resource_name: str) -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as f:
        with zipfile.ZipFile(str(TEST_RESOURCES), "r") as zip_ref:
            zip_ref.extractall(f)
            ret = Path(f) / resource_name
            assert ret.is_dir(), ret
            yield ret


def run_command_and_return_persisted_metadata(command, include_path=False):
    with tempfile.TemporaryDirectory(delete=False) as f:
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT_DIR / "src"
        subprocess.check_output(command(f), env=env, stderr=subprocess.STDOUT)
        actual = json.load(open(f"{f}/.ir-metadata", "r"))
        actual["cpuinfo"] = {k: v for k, v in actual["cpuinfo"].items() if k == "arch"}
        actual["sys"]["executable"] = "python3" if "python3" in actual["sys"]["executable"] else "UNEXPECTED"
        actual["sys"]["version_info"] = "3.XY.XY" if actual["sys"]["version_info"].startswith("3.") else "UNEXPECTED"
        actual["sys"]["argv"] = [i.split("/")[-1] for i in actual["sys"]["argv"] if "example" in i]
        actual["platform"] = {k: "OMITTED" for k in actual["platform"].keys()}
        actual["sys"]["modules"] = [i for i in actual["sys"]["modules"] if "terrier" in i]
        actual["pkg_resources"] = [i for i in actual["pkg_resources"] if "python-terrier" in i]
        if "codecarbon_emissions" in actual:
            actual["codecarbon_emissions"] = "OMMITTED."
        if "notebook" in actual:
            actual["notebook"] = "OMMITTED."

        if include_path:
            actual['path'] = Path(f)

        return actual


class PythonScriptApprovalTests(unittest.TestCase):
    def test_for_valid_git_repo(self):
        with resource("pyterrier") as pyterrier_dir:
            actual = run_command_and_return_persisted_metadata(
                lambda i: ["python3", f"{pyterrier_dir}/example-script.py", i]
            )

            verify_as_json(actual)

    def test_for_jupyter_notebook_in_valid_git_repo(self):
        with resource("pyterrier") as pyterrier_dir:
            cmd = "runnb --allow-not-trusted example-notebook.ipynb"
            actual = run_command_and_return_persisted_metadata(
                lambda i: [
                    "bash",
                    "-c",
                    f"cd {pyterrier_dir} && {cmd} && cp .ir-metadata {i}/.ir-metadata",
                ]
            )

            verify_as_json(actual)

    def test_for_valid_git_repo_without_emissions(self):
        with resource("pyterrier") as pyterrier_dir:
            actual = run_command_and_return_persisted_metadata(
                lambda i: ["python3", f"{pyterrier_dir}/example-script-without-emissions.py", i]
            )

            verify_as_json(actual)

    def test_for_pyterrier_fails_if_not_in_git(self):
        with resource("pyterrier") as pyterrier_dir:
            shutil.rmtree(pyterrier_dir / ".git")

            with self.assertRaises(subprocess.CalledProcessError) as context:
                run_command_and_return_persisted_metadata(
                    lambda i: ["python3", f"{pyterrier_dir}/example-script.py", i]
                )

            self.assertIn("InvalidGitRepositoryError", repr(context.exception.stdout))
