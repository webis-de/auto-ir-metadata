import tempfile
import unittest
import subprocess
import os
import pathlib
ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
EXAMPLE_DIR = ROOT_DIR / 'examples'

class PythonScriptApprovalTests(unittest.TestCase):
    def test_for_valid_git_repo(self):
        with tempfile.NamedTemporaryFile() as f:
            env = os.environ.copy()
            env['PYTHONPATH'] = ROOT_DIR
            subprocess.check_output([f"{EXAMPLE_DIR}/pyterrier/example-script.py", f.name], env=env)

