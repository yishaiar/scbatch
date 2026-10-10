"""ArcSinh transformation entrypoint."""

from anndata import AnnData
import numpy as np

from ..datasets import get_sample_data_mask


def sample_arcsinh(sample_data: np.ndarray, cofactor: float) -> np.ndarray:
    """Apply ArcSinh to sample"""
    return np.arcsinh(sample_data / cofactor)


kwargs = {"cofactor": 5.0}


def arcsinh(
    adata: AnnData,
    func=sample_arcsinh,
) -> AnnData:
    """ArcSinh each original sample in the supplied AnnData in place."""
    if adata.X is None:
        raise ValueError("arcsinh requires adata.X to contain a matrix.")
    if not isinstance(adata.X, np.ndarray):
        raise TypeError("arcsinh currently requires adata.X to be a NumPy array.")

    X = adata.X

    sample_keys = adata.obs[["batch_index", "sample_index"]].drop_duplicates()
    for batch_index, sample_index in sample_keys.itertuples(index=False, name=None):
        sample_mask = get_sample_data_mask(adata, int(batch_index), int(sample_index))
        X[sample_mask.to_numpy()] = func(X[sample_mask.to_numpy()], **kwargs)
    adata.X = X
    return adata


if __name__ == "__main__":
    from ..datasets.demo import load_demo

    adata = load_demo()
    arcsinh(adata)
    print(adata)
