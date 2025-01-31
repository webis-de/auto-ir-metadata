import unittest
from pathlib import Path

from auto_ir_metadata.utils import _executed_file_from_stacktrace, get_url_of_git_repo

ROOT_DIR = Path(__file__).parent.parent.resolve()


class TestUtilityFunctions(unittest.TestCase):
    def test_file_is_extracted(self):
        expected = set(["pytest", "run_pytest_script"])
        actual = _executed_file_from_stacktrace().stem
        self.assertIn(actual, expected)

    def test_git_link_is_failsave(self):
        expected = None
        metadata = {}

        actual = get_url_of_git_repo(metadata)

        self.assertEqual(expected, actual)

    def test_git_link_for_ssh(self):
        expected = 'https://github.com/OpenWebSearch/wows-code/tree/3377c12d5c0a9cccf99f8db6fc4cf1c9d3596b8f'
        metadata = {"git": {
            "commit": "3377c12d5c0a9cccf99f8db6fc4cf1c9d3596b8f",
            "active_branch": "main",
            "remotes": {"origin": "git@github.com:OpenWebSearch/wows-code.git"}
            }
        }

        actual = get_url_of_git_repo(metadata)

        self.assertEqual(expected, actual)

    def test_git_link_for_http(self):
        expected = 'https://github.com/OpenWebSearch/wows-code/tree/3377c12d5c0a9cccf99f8db6fc4cf1c9d3596b8f'
        metadata = {"git": {
            "commit": "3377c12d5c0a9cccf99f8db6fc4cf1c9d3596b8f",
            "active_branch": "main",
            "remotes": {"origin": "https://github.com/OpenWebSearch/wows-code.git"}
            }
        }

        actual = get_url_of_git_repo(metadata)

        self.assertEqual(expected, actual)