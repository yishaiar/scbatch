"""Harmony batch-correction entrypoint."""

from anndata import AnnData


def batch_correct_harmony(
    adata: AnnData,
) -> AnnData:
    """Correct batches with Harmony.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_harmony is not implemented; returning AnnData unchanged.")
    return adata


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_harmony(adata)
    print(adata)
