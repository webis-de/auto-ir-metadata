import tempfile
import unittest


class PythonScriptApprovalTests(unittest.TestCase):
    def test_for_valid_git_repo(self):
        with tempfile.NamedTemporaryFile() as f:
            pass
