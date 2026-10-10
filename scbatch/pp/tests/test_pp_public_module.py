"""Public API and pipeline-contract tests for preprocessing."""

import unittest
from collections.abc import Callable
from inspect import signature
from typing import Any, cast
from unittest import mock

import numpy as np
import scbatch
from anndata import AnnData
from scipy import sparse


def _adata() -> AnnData:
    """Create a pipeline-ready dense AnnData object."""
    return AnnData(
        X=np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]),
        obs={"batch_index": [0, 0, 0], "sample_index": [0, 0, 0]},
    )


def _record_stage(stages: list[str], name: str) -> Callable[..., AnnData]:
    """Return a callback that records and changes the current matrix."""

    def callback(adata: AnnData, **_: object) -> AnnData:
        stages.append(name)
        matrix = cast(Any, adata.X)
        if sparse.issparse(matrix):
            adata.X = matrix * 2
        else:
            adata.X = np.asarray(matrix) + 1
        return adata

    return callback


class TestPreprocessingNamespace(unittest.TestCase):
    """Verify the public namespace exposes only scbatch-owned functions."""

    def test_package_exposes_only_custom_preprocessing_functions(self) -> None:
        self.assertTrue(callable(scbatch.pp.arcsinh))
        self.assertTrue(callable(scbatch.pp.normalize_core))
        self.assertFalse(hasattr(scbatch.pp, "neighbors"))
        self.assertFalse(hasattr(scbatch.pp, "scale"))

    def test_package_exports_root_pipeline(self) -> None:
        self.assertTrue(callable(scbatch.run_pipeline))

    def test_batch_correct_rejects_unknown_method(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown batch-correction method"):
            scbatch.pp.batch_correct(_adata(), method="unknown_method")

    def test_batch_corrector_remains_predictor_alias(self) -> None:
        self.assertIs(scbatch.pp.BatchCorrector, scbatch.pp.BatchCorrectionPredictor)


class TestMatrixPlaceholderFunctions(unittest.TestCase):
    """Verify transformations mutate the supplied AnnData correctly."""

    def test_arcsinh_transforms_the_current_matrix(self) -> None:
        adata = _adata()
        original = cast(Any, adata.X).copy()

        result = scbatch.pp.arcsinh(adata)

        self.assertIs(result, adata)
        np.testing.assert_allclose(cast(Any, adata.X), np.arcsinh(original / 5.0))

    def test_normalize_core_adds_one_to_the_current_matrix(self) -> None:
        adata = _adata()

        result = scbatch.pp.normalize_core(adata)

        self.assertIs(result, adata)
        np.testing.assert_array_equal(cast(Any, adata.X), [[2.0, 3.0], [4.0, 5.0], [6.0, 7.0]])

    def test_qq_batch_correction_adds_one_to_the_current_matrix(self) -> None:
        adata = _adata()

        result = scbatch.pp.batch_correct_qq(adata)

        self.assertIs(result, adata)
        np.testing.assert_array_equal(cast(Any, adata.X), [[2.0, 3.0], [4.0, 5.0], [6.0, 7.0]])

    def test_qq_densifies_sparse_input_when_adding_one(self) -> None:
        adata = AnnData(X=sparse.csr_matrix([[0.0, 2.0]]))

        scbatch.pp.batch_correct_qq(adata)

        self.assertFalse(sparse.issparse(adata.X))
        np.testing.assert_array_equal(cast(Any, adata.X), [[1.0, 3.0]])

    def test_placeholder_functions_reject_missing_matrix(self) -> None:
        for function in (
            scbatch.pp.arcsinh,
            scbatch.pp.normalize_core,
            scbatch.pp.batch_correct_qq,
        ):
            with self.subTest(function=function.__name__):
                adata = AnnData(X=None, shape=(2, 2))

                with self.assertRaisesRegex(ValueError, "adata.X"):
                    function(adata)


class TestPipelineContract(unittest.TestCase):
    """Verify layer snapshots and Scanpy ownership in the pipeline."""

    def _run_pipeline(self, adata: AnnData) -> tuple[AnnData, list[str]]:
        stages: list[str] = []
        with (
            mock.patch("scbatch.pipeline.pp.gating", _record_stage(stages, "gating")),
            mock.patch("scbatch.pipeline.pp.arcsinh", _record_stage(stages, "arcsinh")),
            mock.patch("scbatch.pipeline.pp.batch_correct", _record_stage(stages, "batch")),
            mock.patch("scbatch.pipeline.pp.normalize_core", _record_stage(stages, "normalize")),
            mock.patch("scbatch.pipeline.sc.pp.scale", _record_stage(stages, "scale")),
            mock.patch("scbatch.pipeline.sc.pp.neighbors", _record_stage(stages, "neighbors")),
            mock.patch("scbatch.pipeline.sc.tl.umap", _record_stage(stages, "umap")),
            mock.patch("scbatch.pipeline.sc.tl.leiden", _record_stage(stages, "leiden")),
        ):
            return scbatch.run_pipeline(adata), stages

    def test_pipeline_snapshots_each_matrix_stage(self) -> None:
        result, stages = self._run_pipeline(_adata())

        self.assertEqual(
            stages,
            [
                "gating",
                "arcsinh",
                "batch",
                "normalize",
                "scale",
                "neighbors",
                "umap",
                "neighbors",
                "leiden",
            ],
        )
        self.assertEqual(
            list(result.layers),
            [
                "input",
                "Gated",
                "arcsinh",
                "batch_corrected",
                "core_normalized",
                "scaled",
                "umap",
                "leiden",
            ],
        )
        np.testing.assert_array_equal(
            cast(Any, result.layers["input"]),
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        )
        np.testing.assert_array_equal(
            cast(Any, result.layers["scaled"]),
            [[6.0, 7.0], [8.0, 9.0], [10.0, 11.0]],
        )

    def test_pipeline_layers_do_not_alias_the_working_matrix(self) -> None:
        result, _ = self._run_pipeline(_adata())

        matrix = cast(Any, result.X)
        matrix[0, 0] = -100.0

        self.assertEqual(cast(Any, result.layers["scaled"])[0, 0], 6.0)
        self.assertEqual(cast(Any, result.layers["input"])[0, 0], 1.0)

    def test_pipeline_mutates_the_supplied_object(self) -> None:
        adata = _adata()
        result, _ = self._run_pipeline(adata)

        self.assertIs(result, adata)
        np.testing.assert_array_equal(
            cast(Any, adata.X),
            [[10.0, 11.0], [12.0, 13.0], [14.0, 15.0]],
        )
        np.testing.assert_array_equal(
            cast(Any, adata.layers["input"]),
            [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        )

    def test_pipeline_preserves_sparse_snapshots(self) -> None:
        adata = AnnData(X=sparse.csr_matrix([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]))

        result, _ = self._run_pipeline(adata)

        self.assertTrue(sparse.issparse(result.layers["input"]))
        self.assertTrue(sparse.issparse(result.layers["scaled"]))

    def test_pipeline_rejects_missing_matrix(self) -> None:
        adata = AnnData(X=None, shape=(2, 2))

        with self.assertRaisesRegex(ValueError, "adata.X"):
            scbatch.run_pipeline(adata)

    def test_pipeline_uses_dbscan_branch(self) -> None:
        adata = _adata()
        with (
            mock.patch("scbatch.pipeline.tl.dbscan", return_value=adata) as dbscan,
            mock.patch("scbatch.pipeline.pp.gating", return_value=adata),
            mock.patch("scbatch.pipeline.sc.pp.scale"),
            mock.patch("scbatch.pipeline.sc.pp.neighbors") as neighbors,
            mock.patch("scbatch.pipeline.sc.tl.umap") as umap,
            mock.patch("scbatch.pipeline.sc.tl.leiden") as leiden,
        ):
            result = scbatch.run_pipeline(adata, clustering_is_leiden=False)

        self.assertIs(result, adata)
        dbscan.assert_called_once_with(adata, use_rep="X_umap")
        neighbors.assert_called_once_with(adata)
        umap.assert_called_once_with(adata)
        leiden.assert_not_called()
        self.assertIn("umap", adata.layers)
        self.assertIn("dbscan", adata.layers)

    def test_pipeline_relies_on_scanpy_standard_analysis_slots(self) -> None:
        adata = _adata()
        with mock.patch("scbatch.pipeline.pp.gating", return_value=adata):
            with mock.patch("scbatch.pipeline.sc.pp.scale"):
                with mock.patch("scbatch.pipeline.sc.pp.neighbors") as neighbors:
                    with mock.patch("scbatch.pipeline.sc.tl.umap") as umap:
                        with mock.patch("scbatch.pipeline.sc.tl.leiden") as leiden:
                            scbatch.run_pipeline(adata)

        self.assertEqual(
            neighbors.call_args_list,
            [mock.call(adata), mock.call(adata, use_rep="X_umap")],
        )
        umap.assert_called_once_with(adata)
        leiden.assert_called_once_with(adata)
        self.assertNotIn("neighbors", adata.layers)
        self.assertIn("umap", adata.layers)
        self.assertIn("leiden", adata.layers)
