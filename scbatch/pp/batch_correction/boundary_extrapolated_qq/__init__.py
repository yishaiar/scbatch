"""Boundary-extrapolated QQ batch-correction method."""

from anndata import AnnData


def batch_correct_boundary_extrapolated_qq(
    adata: AnnData,
) -> AnnData:
    """Correct batches with boundary-extrapolated QQ mapping.

    This scaffold preserves the input.
    """
    print(
        "scbatch.pp.batch_correct_boundary_extrapolated_qq is not implemented; "
        "returning AnnData unchanged."
    )
    return adata
