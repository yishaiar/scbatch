"""FastMNN batch-correction method."""

from anndata import AnnData


def batch_correct_fastmnn(
    adata: AnnData,
) -> AnnData:
    """Correct batches with FastMNN.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_fastmnn is not implemented; returning AnnData unchanged.")
    return adata
