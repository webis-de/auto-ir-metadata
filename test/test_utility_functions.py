import importlib
import pathlib
import unittest
from pathlib import Path

from git import InvalidGitRepositoryError

from autometadata import _executed_file_from_stacktrace, collect_git_repo_metadata, get_gpu_info

ROOT_DIR = importlib.resources.files() / '..'


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
        self.assertIsNotNone(collect_git_repo_metadata(ROOT_DIR / "src" / "autometadata"))

    def test_get_gpus(self):
        self.assertIsNotNone(get_gpu_info())
