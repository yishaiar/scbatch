"""Quantile-quantile correction entrypoint."""

from typing import Any, cast

from anndata import AnnData
from scipy import sparse


def batch_correct_qq(
    adata: AnnData,
) -> AnnData:
    """Add one to the current matrix and store the result in ``adata.X``.

    Sparse input is densified because adding one changes every implicit zero.
    """
    matrix = cast(Any, adata.X)
    if matrix is None:
        raise ValueError("batch_correct_qq requires adata.X to contain a matrix.")
    adata.X = matrix.toarray() + 1 if sparse.issparse(matrix) else matrix + 1
    return adata


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_qq(adata)
    print(adata)
