"""cyCombine batch-correction method."""

from anndata import AnnData


def batch_correct_cycombine(
    adata: AnnData,
) -> AnnData:
    """Correct batches with cyCombine.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_cycombine is not implemented; returning AnnData unchanged.")
    return adata
