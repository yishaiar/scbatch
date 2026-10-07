"""Public namespace tests for tools."""

import unittest

import scbatch


class TestToolsNamespace(unittest.TestCase):
    def test_package_exposes_tools_namespace(self) -> None:
        self.assertIsNotNone(scbatch.tl)
