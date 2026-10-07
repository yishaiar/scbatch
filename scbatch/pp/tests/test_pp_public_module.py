"""Public namespace tests for preprocessing."""

import unittest

import scbatch


class TestPreprocessingNamespace(unittest.TestCase):
    def test_package_exposes_preprocessing_namespace(self) -> None:
        self.assertIsNotNone(scbatch.pp)
