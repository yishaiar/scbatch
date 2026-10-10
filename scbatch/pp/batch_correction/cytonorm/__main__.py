"""CytoNorm batch-correction entrypoint."""

from anndata import AnnData


def batch_correct_cytonorm(
    adata: AnnData,
) -> AnnData:
    """Correct batches with CytoNorm.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_cytonorm is not implemented; returning AnnData unchanged.")
    return adata


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_cytonorm(adata)
    print(adata)
