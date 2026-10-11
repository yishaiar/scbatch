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
    """Run preprocessing, embedding, and clustering in place.

    Matrix stages are preserved in ``adata.layers``. Scanpy stores the graph
    and embedding in its standard AnnData slots.
    """
    if adata.X is None:
        raise ValueError("run_pipeline requires adata.X to contain a matrix.")

    adata.layers["input"] = cast(Any, adata.X).copy()
    pp.gating(adata)
    if adata.X is None:
        raise ValueError("Gating returned an AnnData without a matrix in adata.X.")
    adata.layers["Gated"] = cast(Any, adata.X).copy()

    pp.arcsinh(adata)
    adata.layers["arcsinh"] = cast(Any, adata.X).copy()
    pp.batch_correct(adata, method=method)
    adata.layers["batch_corrected"] = cast(Any, adata.X).copy()
    pp.normalize_core(adata)
    adata.layers["core_normalized"] = cast(Any, adata.X).copy()

    sc.pp.scale(adata)
    adata.layers["scaled"] = cast(Any, adata.X).copy()
    sc.pp.neighbors(adata)
    sc.tl.umap(adata)
    adata.layers["umap"] = cast(Any, adata.X).copy()

    if clustering_is_leiden:
        sc.pp.neighbors(adata, use_rep="X_umap")
        sc.tl.leiden(adata)
        adata.layers["leiden"] = cast(Any, adata.X).copy()
    else:
        tl.dbscan(adata, use_rep="X_umap")
        adata.layers["dbscan"] = cast(Any, adata.X).copy()
    return adata
