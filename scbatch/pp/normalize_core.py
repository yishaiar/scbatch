"""Core-control normalization entrypoint."""

from anndata import AnnData
import numpy as np

from ..datasets import get_sample_data_mask


kwargs = {"coreFetures": ["H3.3", "H4"]}


def sample_noramalize_core(
    sample_data: np.ndarray,
    coreFetures: list[str],
) -> np.ndarray:
    """Apply core-control normalization to one sample."""
    return sample_data + 1


def normalize_core(adata: AnnData, func=sample_noramalize_core) -> AnnData:
    """Normalize each original sample in the supplied AnnData in place."""
    if adata.X is None:
        raise ValueError("normalize_core requires adata.X to contain a matrix.")
    if not isinstance(adata.X, np.ndarray):
        raise TypeError("normalize_core currently requires adata.X to be a NumPy array.")

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
    adata = normalize_core(adata)
    print(adata)
