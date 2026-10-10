"""Boundary-extrapolated quantile-quantile correction entrypoint."""

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


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_boundary_extrapolated_qq(adata)
    print(adata)
