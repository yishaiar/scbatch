"""Preprocessing workflow orchestration."""

from typing import Any, cast

from anndata import AnnData

from .arcsinh import arcsinh
from .batch_correction import DEFAULT_CORRECTION_METHOD, batch_correct
from .gating import gating
from .normalize_core import normalize_core


def run_pre_processing(
    adata: AnnData,
    method: str = DEFAULT_CORRECTION_METHOD,
) -> AnnData:
    """Run the scbatch preprocessing pipeline.

    Matrix stages:
        1. Save the starting matrix to ``layers["input"]``.
        2. Apply the current per-sample gate and save to ``layers["Gated"]``.
        3. Apply ArcSinh transformation and save to ``layers["arcsinh"]``.
        4. Apply batch correction and save to ``layers["batch_corrected"]``.
        5. Apply core normalization and save to ``layers["core_normalized"]``.
    This function performs preprocessing through core normalization. Scaling,
    embedding, and clustering are not part of this workflow.
    """
    if adata.X is None:
        raise ValueError("run_pipeline requires adata.X to contain a matrix.")

    # Matrix pipeline: every operation changes adata.X, then X is copied to
    # its same-shaped layer. Filtering also subsets all existing layers.
    # 1. Preserve the input matrix before any filtering or transformation.
    adata.layers["input"] = cast(Any, adata.X).copy()

    # 2. Apply the current per-sample gate.
    # This function mutates adata, removing values beyond the per-sample
    # 0.001 and 0.9999 quantiles.
    adata = gating(adata)
    if adata.X is None:
        raise ValueError("Gating returned an AnnData without a matrix in adata.X.")
    adata.layers["Gated"] = cast(Any, adata.X).copy()

    # 3. Transform X with ArcSinh and preserve the transformed matrix.
    arcsinh(adata)
    adata.layers["arcsinh"] = cast(Any, adata.X).copy()

    # 4. Correct X and preserve the corrected matrix.
    batch_correct(adata, method=method)
    adata.layers["batch_corrected"] = cast(Any, adata.X).copy()

    # 5. Normalize and preserve the normalized matrix.
    normalize_core(adata)
    adata.layers["core_normalized"] = cast(Any, adata.X).copy()
    return adata


if __name__ == "__main__":
    from ..datasets.demo import load_demo

    demo_adata = load_demo()
    adata = run_pre_processing(demo_adata)
