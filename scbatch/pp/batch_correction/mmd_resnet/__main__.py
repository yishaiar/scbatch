"""MMD-ResNet batch-correction entrypoint."""

from anndata import AnnData


def batch_correct_mmd_resnet(
    adata: AnnData,
) -> AnnData:
    """Correct batches with MMD-ResNet.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_mmd_resnet is not implemented; returning AnnData unchanged.")
    return adata


if __name__ == "__main__":
    from ....datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct_mmd_resnet(adata)
    print(adata)
