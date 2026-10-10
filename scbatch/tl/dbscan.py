"""DBSCAN clustering entrypoint."""

from anndata import AnnData


def dbscan(
    adata: AnnData,
    use_rep: str = "X_umap",
) -> AnnData:
    """Cluster the current AnnData representation with scbatch DBSCAN.

    The current scaffold preserves its input. ``run_pipeline`` owns matrix
    layer snapshots and will later record DBSCAN labels in ``adata.obs``.
    """
    _ = use_rep
    print("scbatch.tl.dbscan is not implemented; returning AnnData unchanged.")
    return adata
