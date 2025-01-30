import unittest
from pathlib import Path

from approvaltests import verify_as_json

from auto_ir_metadata import load_ir_metadata as load_ir_metadata_to_test

ROOT_DIR = Path(__file__).parent.parent.resolve()
TEST_RESOURCES = ROOT_DIR / "test" / "resources"
FIELDS_TO_OMIT = [
    'sys', 'pkg_resources', 'platform', 'cpuinfo', 'file', 'notebook', 'gpus',
    'notebook_html'
]


def load_ir_metadata(subdirectory):
    ret = load_ir_metadata_to_test(TEST_RESOURCES / subdirectory)

    for field_to_omit in FIELDS_TO_OMIT:
        if field_to_omit in ret:
            ret[field_to_omit] = 'OMITTED'

    return ret


class TestParsingOfMetadata(unittest.TestCase):
    def test_loading_of_metadata_from_notebook_directory(self):
        actual = load_ir_metadata("example-ir-metadata")

        verify_as_json(actual)

    def test_loading_of_metadata_from_file_in_notebook_directory(self):
        actual = load_ir_metadata("example-ir-metadata/.ir-metadata")

        verify_as_json(actual)

    def test_loading_of_metadata_from_file_with_invalid_notebook(self):
        actual = load_ir_metadata("example-ir-metadata/ir-metadata-invalid-notebook")

        verify_as_json(actual)
