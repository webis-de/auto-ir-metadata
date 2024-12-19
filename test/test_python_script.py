import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
from approvaltests import verify_as_json

EXAMPLE_DIR = ROOT_DIR / "examples"
import json


def run_command_and_return_persisted_metadata(command):
    with tempfile.TemporaryDirectory() as f:
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT_DIR
        subprocess.check_output(command(f), env=env)
        actual = json.load(open(f"{f}/.ir-metadata", "r"))
        actual["sys"]["executable"] = "python3" if "python3" in actual["sys"]["executable"] else "UNEXPECTED"
        actual["sys"]["version_info"] = "3.XY.XY" if actual["sys"]["version_info"].startswith("3.") else "UNEXPECTED"
        actual["sys"]["argv"] = [i.split("/examples/")[1] for i in actual["sys"]["argv"] if "/examples/" in i]
        actual["sys"]["modules"] = [i for i in actual["sys"]["modules"] if "terrier" in i]
        actual["pkg_resources"] = [i for i in actual["pkg_resources"] if "python-terrier" in i]
        return actual


class PythonScriptApprovalTests(unittest.TestCase):
    def test_for_valid_git_repo(self):
        actual = run_command_and_return_persisted_metadata(lambda i: [f"{EXAMPLE_DIR}/pyterrier/example-script.py", i])
        verify_as_json(actual)
