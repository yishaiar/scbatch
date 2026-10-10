"""cyCombine batch-correction entrypoint."""

from anndata import AnnData


def batch_correct_cycombine(
    adata: AnnData,
) -> AnnData:
    """Correct batches with cyCombine.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_cycombine is not implemented; returning AnnData unchanged.")
    return adata


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_cycombine(adata)
    print(adata)
