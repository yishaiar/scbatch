"""Public namespace tests for datasets."""

import unittest

import scbatch


class TestDatasetsNamespace(unittest.TestCase):
    def test_package_exposes_datasets_namespace(self) -> None:
        self.assertIsNotNone(scbatch.datasets)
