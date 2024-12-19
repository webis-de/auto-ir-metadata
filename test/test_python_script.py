import json
import os
import pathlib
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from approvaltests import verify_as_json

TEST_RESOURCES = pathlib.Path(__file__).parent.parent.resolve() / "test" / "test-resources.zip"


def resource(resource_name):
    with tempfile.TemporaryDirectory(delete=False) as f:
        with zipfile.ZipFile(TEST_RESOURCES, "r") as zip_ref:
            zip_ref.extractall(f)
            ret = Path(f) / resource_name
            assert ret.is_dir(), ret
            return ret


def run_command_and_return_persisted_metadata(command):
    with tempfile.TemporaryDirectory() as f:
        env = os.environ.copy()
        subprocess.check_output(command(f), env=env)
        actual = json.load(open(f"{f}/.ir-metadata", "r"))
        actual["sys"]["executable"] = "python3" if "python3" in actual["sys"]["executable"] else "UNEXPECTED"
        actual["sys"]["version_info"] = "3.XY.XY" if actual["sys"]["version_info"].startswith("3.") else "UNEXPECTED"
        actual["sys"]["argv"] = [i.split("/")[-1] for i in actual["sys"]["argv"] if "example" in i]
        actual["sys"]["modules"] = [i for i in actual["sys"]["modules"] if "terrier" in i]
        actual["pkg_resources"] = [i for i in actual["pkg_resources"] if "python-terrier" in i]
        return actual


class PythonScriptApprovalTests(unittest.TestCase):
    def test_for_valid_git_repo(self):
        pyterrier_dir = resource("pyterrier")

        actual = run_command_and_return_persisted_metadata(
            lambda i: ["python3", f"{pyterrier_dir}/example-script.py", i]
        )
        verify_as_json(actual)
