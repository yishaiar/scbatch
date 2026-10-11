"""CytoNorm batch-correction method."""

from anndata import AnnData


def batch_correct_cytonorm(
    adata: AnnData,
) -> AnnData:
    """Correct batches with CytoNorm.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_cytonorm is not implemented; returning AnnData unchanged.")
    return adata
