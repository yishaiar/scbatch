"""Harmony batch-correction method."""

from anndata import AnnData


def batch_correct_harmony(
    adata: AnnData,
) -> AnnData:
    """Correct batches with Harmony.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_harmony is not implemented; returning AnnData unchanged.")
    return adata
