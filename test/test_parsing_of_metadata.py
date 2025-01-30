import unittest

from auto_ir_metadata import load_ir_metadata

from .test_python_script import resource, run_command_and_return_persisted_metadata


class TestParsingOfMetadata(unittest.TestCase):
    def test_for_jupyter_notebook_in_valid_git_repo(self):
        with resource("pyterrier") as pyterrier_dir:
            cmd = "runnb --allow-not-trusted example-notebook.ipynb"
            metadata_path = run_command_and_return_persisted_metadata(
                lambda i: [
                    "bash",
                    "-c",
                    f"cd {pyterrier_dir} && {cmd} && cp .ir-metadata {i}/.ir-metadata",
                ],
                include_path=True
            )['path']
            actual = load_ir_metadata(metadata_path)

            verify_as_json(actual)