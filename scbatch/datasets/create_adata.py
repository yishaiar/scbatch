"""Build AnnData objects from batched NumPy or pandas samples.

Batch, sample, and anchor-pair metadata are added to observations.
"""

from typing import Any

import numpy as np
import pandas as pd
from anndata import AnnData
from .utils import adata_columns


def create_adata_from_dataset(
    dataset: list[list[Any]],
    anchor_pairs: list[dict[str, int]],
) -> AnnData:
    """Combine batches of sample matrices into one annotated AnnData object.

    Each sample is a two-dimensional observations-by-markers NumPy array or
    pandas DataFrame. ``anchor_pairs`` uses zero-based batch and sample indexes.
    """
    _validate_dataset(dataset)
    batches: list[tuple[str, list[np.ndarray | pd.DataFrame]]] = [
        (f"Batch_{batch_index}", list(samples)) for batch_index, samples in enumerate(dataset)
    ]
    sample_arrays = []
    for _, samples in batches:
        for matrix in samples:
            sample_array = matrix.to_numpy() if isinstance(matrix, pd.DataFrame) else matrix
            sample_arrays.append(sample_array)
    X = np.concatenate(sample_arrays, axis=0)
    adata = AnnData(X=X)

    adata.var_names = _marker_names(dataset)

    # adata.uns["anchor_pairs"] = anchor_pairs
    adata.obs = _observation_metadata(batches, anchor_pairs)

    return adata


def _marker_names(dataset: list[list[Any]]) -> list[str]:
    """Use DataFrame column labels or generate names for array markers."""
    sample = dataset[0][0]
    if isinstance(sample, pd.DataFrame):
        return [str(column) for column in sample.columns]
    # it's an numpy array so take shape
    return [f"marker_{index}" for index in range(1, sample.shape[1] + 1)]


def _validate_dataset(
    dataset: list[list[np.ndarray | pd.DataFrame]],
) -> None:
    """Check that samples are non-empty matrices with the same marker count."""
    if not dataset:
        raise ValueError("dataset must contain at least one batch.")
    marker_count: int | None = None
    for samples in dataset:
        if not samples:
            raise ValueError("Each batch must contain at least one sample.")
        for matrix in samples:
            if not isinstance(matrix, (np.ndarray, pd.DataFrame)):
                raise ValueError("Each sample must be a NumPy array or pandas DataFrame.")
            if matrix.ndim != 2 or matrix.shape[0] == 0:
                raise ValueError("Each sample must be a non-empty two-dimensional matrix.")
            if matrix.shape[1] == 0:
                raise ValueError("Sample matrices must contain at least one marker.")
            if marker_count is None:
                marker_count = matrix.shape[1]
            elif matrix.shape[1] != marker_count:
                raise ValueError("All sample matrices must have the same marker count.")


def _observation_metadata(
    batches: list[tuple[str, list[np.ndarray | pd.DataFrame]]],
    anchor_pairs: list[dict[str, int]],
) -> pd.DataFrame:
    """Build one metadata row per observation and record each sample's anchor.

    Anchor pairs use zero-based batch and sample indexes. Their endpoints must
    exist, differ, and appear in no other pair.
    """
    anchor_targets: dict[tuple[int, int], tuple[int, int]] = {}
    for pair in anchor_pairs:
        source = (pair["from_batch"], pair["from_sample"])
        target = (pair["to_batch"], pair["to_sample"])
        for batch_index, sample_index in (source, target):
            if not 0 <= batch_index < len(batches):
                raise ValueError(f"batch index {batch_index} is outside dataset bounds.")
            batch_name, samples = batches[batch_index]
            if not 0 <= sample_index < len(samples):
                raise ValueError(
                    f"sample index {sample_index} is outside batch {batch_name!r} bounds."
                )
        if source == target or source in anchor_targets or target in anchor_targets:
            raise ValueError("An anchor sample may appear in exactly one anchor pair.")
        anchor_targets[source] = target
        anchor_targets[target] = source

    observations: list[dict[str, Any]] = []
    for batch_index, (batch_name, samples) in enumerate(batches):
        for sample_index, matrix in enumerate(samples):
            anchor = anchor_targets.get((batch_index, sample_index))
            sample_values = (
                batch_name,
                batch_index,
                str(sample_index),
                sample_index,
                f"batch_{batch_name}_sample_{sample_index}",
                anchor is not None,
                "not_an_anchor" if anchor is None else batches[anchor[0]][0],
                "not_an_anchor" if anchor is None else str(anchor[1]),
            )
            # Keep these values in the same order as the shared observation columns.
            sample_metadata = dict(zip(adata_columns, sample_values, strict=True))
            # -1 marks an unpaired sample; otherwise store its partner's sample index.
            partner_index = -1 if anchor is None else anchor[1]
            sample_metadata.update(
                anchor_to_batch_index=-1 if anchor is None else anchor[0],
                anchor_to_sample_index=partner_index,
            )

            # AnnData stores one obs row per observation, so repeat this sample's metadata.
            observations.extend(sample_metadata.copy() for _ in range(matrix.shape[0]))
    observation_table = pd.DataFrame.from_records(observations)
    # AnnData requires string observation indexes. Keep the standard compact
    # integer-like labels instead of exposing a synthetic observation-name field.
    observation_table.index = pd.Index([str(index) for index in range(len(observation_table))])
    return observation_table
