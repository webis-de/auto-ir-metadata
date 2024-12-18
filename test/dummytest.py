"""
This file only exists to have a dummy test during initial setup. Please remove once actual tests have been added!
"""

import unittest

from autometadata import dummy


class TestDummy(unittest.TestCase):

    def test_dummy(self):
        self.assertEqual(dummy(), 42)
