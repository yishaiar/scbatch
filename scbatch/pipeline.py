"""End-to-end scbatch workflow orchestration."""

from typing import Any, cast

import scanpy as sc
from anndata import AnnData

from . import pp, tl
from .pp.batch_correction.batch_correction_config import DEFAULT_CORRECTION_METHOD


def run_pipeline(
    adata: AnnData,
    method: str = DEFAULT_CORRECTION_METHOD,
    clustering_is_leiden: bool = True,
) -> AnnData:
    """Run the scbatch preprocessing pipeline.

    Matrix stages:
        1. Save the starting matrix to ``layers["input"]``.
        2. Apply the current per-sample gate and save to ``layers["Gated"]``.
        3. Apply ArcSinh transformation and save to ``layers["arcsinh"]``.
        4. Apply batch correction and save to ``layers["batch_corrected"]``.
        5. Apply core normalization and save to ``layers["core_normalized"]``.
        6. Scale and save to ``layers["scaled"]``.
        7. Compute UMAP and save to ``layers["umap"]``.
        8. Find clusters on UMAP using Leiden or DBSCAN and save to
           ``layers["leiden"]`` or ``layers["dbscan"]``.


    Notes:
        This function mutates ``adata``. Gating currently keeps values above
        0.01 and removes values above the per-sample 0.9999 quantile.
        This provisional rule is not validated biological quality control.
    """
    if adata.X is None:
        raise ValueError("run_pipeline requires adata.X to contain a matrix.")

    # Matrix pipeline: every operation changes adata.X, then X is copied to
    # its same-shaped layer. Filtering also subsets all existing layers.
    # 1. Preserve the input matrix before any filtering or transformation.
    adata.layers["input"] = cast(Any, adata.X).copy()

    # 2. Apply the current per-sample gate.
    adata = pp.gating(adata)
    if adata.X is None:
        raise ValueError("Gating returned an AnnData without a matrix in adata.X.")
    adata.layers["Gated"] = cast(Any, adata.X).copy()

    # 3. Transform X with ArcSinh and preserve the transformed matrix.
    pp.arcsinh(adata)
    adata.layers["arcsinh"] = cast(Any, adata.X).copy()

    # 4. Correct X and preserve the corrected matrix.
    pp.batch_correct(adata, method=method)
    adata.layers["batch_corrected"] = cast(Any, adata.X).copy()

    # 5. Normalize and preserve the normalized matrix.
    pp.normalize_core(adata)
    adata.layers["core_normalized"] = cast(Any, adata.X).copy()

    # 6. Scale X across all surviving samples and preserve the matrix used downstream.
    sc.pp.scale(adata)
    adata.layers["scaled"] = cast(Any, adata.X).copy()

    # 7. Create UMAP: build its required neighbors graph, then embed it in 2D.
    sc.pp.neighbors(adata)
    # Default UMAP reads neighbors connectivities and writes coordinates to
    # adata.obsm["X_umap"].
    sc.tl.umap(adata)
    adata.layers["umap"] = cast(Any, adata.X).copy()

    # 8. Cluster cells on UMAP: Leiden uses the neighbors graph; otherwise use DBSCAN.
    if clustering_is_leiden:
        # Default Leiden reads neighbors connectivities and writes labels to obs.
        sc.pp.neighbors(adata, use_rep="X_umap")
        sc.tl.leiden(adata)
        adata.layers["leiden"] = cast(Any, adata.X).copy()

    else:
        # DBSCAN receives the UMAP representation through use_rep.
        tl.dbscan(adata, use_rep="X_umap")
        adata.layers["dbscan"] = cast(Any, adata.X).copy()
    return adata


if __name__ == "__main__":
    from .datasets.demo import load_demo

    demo_adata = load_demo()
    run_pipeline(demo_adata, clustering_is_leiden=False)
