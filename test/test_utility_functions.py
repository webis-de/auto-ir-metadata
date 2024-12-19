import os
import pathlib
import unittest
from pathlib import Path

from git import InvalidGitRepositoryError

from autometadata import _executed_file_from_stacktrace, collect_git_repo_metadata

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()


class TestUtilityFunctions(unittest.TestCase):
    def test_file_is_extracted(self):
        expected = set(["pytest", "run_pytest_script"])
        actual = _executed_file_from_stacktrace().stem
        self.assertTrue(actual in expected, f"{actual} must be in {expected}")

    def test_tmp_is_no_git_repo(self):
        with self.assertRaises(InvalidGitRepositoryError) as context:
            collect_git_repo_metadata(Path("/tmp"))

        self.assertTrue("InvalidGitRepositoryError" not in repr(context))

    def test_with_current_git_repo_root_level(self):
        self.assertIsNotNone(collect_git_repo_metadata(ROOT_DIR))

    def test_with_current_git_repo_multiple_nonroot_level(self):
        self.assertIsNotNone(collect_git_repo_metadata(ROOT_DIR / "src" / "autometadata"))
