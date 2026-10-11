"""MMD-ResNet batch-correction method."""

from anndata import AnnData


def batch_correct_mmd_resnet(
    adata: AnnData,
) -> AnnData:
    """Correct batches with MMD-ResNet.

    This scaffold preserves the input.
    """
    print("scbatch.pp.batch_correct_mmd_resnet is not implemented; returning AnnData unchanged.")
    return adata
