import unittest
from pathlib import Path

from git import InvalidGitRepositoryError

from auto_ir_metadata import (
    _executed_file_from_stacktrace,
    collect_git_repo_metadata,
    get_gpu_info,
    get_url_of_git_repo,
)

ROOT_DIR = Path(__file__).parent.parent.resolve()


class TestUtilityFunctions(unittest.TestCase):
    def test_file_is_extracted(self):
        expected = set(["pytest", "run_pytest_script"])
        actual = _executed_file_from_stacktrace().stem
        self.assertIn(actual, expected)

    def test_tmp_is_no_git_repo(self):
        with self.assertRaises(InvalidGitRepositoryError) as context:
            collect_git_repo_metadata(Path("/tmp"))

        self.assertNotIn("InvalidGitRepositoryError", repr(context))

    def test_with_current_git_repo_root_level(self):
        self.assertIsNotNone(collect_git_repo_metadata(ROOT_DIR))

    def test_with_current_git_repo_multiple_nonroot_level(self):
        self.assertIsNotNone(collect_git_repo_metadata(ROOT_DIR / "src" / "auto_ir_metadata"))

    def test_get_gpus(self):
        self.assertIsNotNone(get_gpu_info())

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