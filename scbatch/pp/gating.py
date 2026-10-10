"""Per-sample core and outlier gating."""

import numpy as np
import pandas as pd
from anndata import AnnData

from ..datasets import get_sample_data_mask

# real value is 5 we now use 0.3 because its a synthetic dataset
kwargs = {"gateValue": 0.01}


def sample_gating(adata: AnnData, sample_mask: pd.Series, gateValue: float) -> np.ndarray:
    """Return a sample-local mask for core and upper-tail outlier gating."""
    sample = np.asarray(adata[sample_mask.to_numpy()].X)
    core_mask = (sample > gateValue).all(axis=1)
    gated = sample[core_mask]
    if gated.size == 0:
        return core_mask

    quantile = np.quantile(gated, 0.9999, axis=0)
    outlier_mask = (gated < quantile).all(axis=1)
    keep_mask = np.zeros(sample.shape[0], dtype=bool)
    keep_mask[np.flatnonzero(core_mask)] = outlier_mask
    return keep_mask


def gating(adata: AnnData, func=sample_gating) -> AnnData:
    """Gate each sample and return the aligned AnnData subset."""
    gated_samples_mask = np.zeros(adata.n_obs, dtype=bool)
    sample_keys = adata.obs[["batch_index", "sample_index"]].drop_duplicates()
    for batch_index, sample_index in sample_keys.itertuples(index=False, name=None):
        # Apply the configured  operation to this sample.
        sample_mask = get_sample_data_mask(adata, int(batch_index), int(sample_index))
        gated_samples_mask[sample_mask.to_numpy()] = func(adata, sample_mask, **kwargs)
    return adata[gated_samples_mask]


if __name__ == "__main__":
    from ..datasets.demo import load_demo

    adata = load_demo()
    adata = gating(adata)
    print(adata)
