"""Public namespace tests for scbatch-specific tools."""

import unittest
from unittest import mock

import numpy as np
import scbatch
from anndata import AnnData


class TestToolsNamespace(unittest.TestCase):
    """Verify only DBSCAN remains owned by the scbatch tool namespace."""

    def test_package_exports_dbscan_only(self) -> None:
        self.assertTrue(callable(scbatch.tl.dbscan))
        self.assertFalse(hasattr(scbatch.tl, "leiden"))
        self.assertFalse(hasattr(scbatch.tl, "umap"))

    def test_dbscan_scaffold_returns_input(self) -> None:
        adata = AnnData(X=np.array([[1.0]]))
        with mock.patch("builtins.print") as printed:
            result = scbatch.tl.dbscan(adata)

        self.assertIs(result, adata)
        printed.assert_called_once()
