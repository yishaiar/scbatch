"""Utilities for inspecting, serializing, and retrieving AnnData samples."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse

adata_columns = [
    "batch",
    "batch_index",
    "sample",
    "sample_index",
    "sample_id",
    "is_anchor",
    "anchor_to_batch",
    "anchor_to_sample",
]


def save_adata_to_json(adata: AnnData, path: str | Path) -> None:
    """Save a dense AnnData object's matrix and annotations as JSON.

    This demo format stores ``X``, ``obs``, ``var``, and marker names. It does
    not serialize layers, embeddings, graphs, raw data, or unstructured data.
    """
    if adata.X is None:
        raise ValueError("AnnData must have an X matrix to save as JSON.")
    if (
        adata.raw is not None
        or adata.layers
        or adata.obsm
        or adata.varm
        or adata.obsp
        or adata.varp
        or adata.uns
    ):
        raise ValueError("JSON export supports only X, obs, and var data.")

    matrix: Any = adata.X
    if sparse.issparse(matrix):
        matrix = matrix.toarray()
    else:
        matrix = np.asarray(matrix)
    payload = {
        "format": "scbatch.adata.v1",
        "X": matrix.tolist(),
        "obs": _serialize_dataframe(adata.obs, include_index=True),
        "var": _serialize_dataframe(adata.var, include_index=False),
        "marker_names": [str(name) for name in adata.var_names],
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, allow_nan=False))


def _serialize_dataframe(frame: pd.DataFrame, include_index: bool) -> dict[str, list[Any]]:
    """Convert a DataFrame's columns and rows to JSON-compatible values."""
    serialized: dict[str, list[Any]] = {
        "columns": [str(column) for column in frame.columns],
        "data": [
            [_json_value(value) for value in row]
            for row in frame.astype(object).to_numpy().tolist()
        ],
    }
    if include_index:
        serialized["index"] = [str(index) for index in frame.index]
    return serialized


def _json_value(value: Any) -> Any:
    """Convert pandas and NumPy scalar values to standard JSON values."""
    if value is None or pd.isna(value):
        return None
    return value.item() if isinstance(value, np.generic) else value


def summarize_samples(adata: AnnData, columns=adata_columns) -> pd.DataFrame:
    """Print marker names and return one metadata row and size per sample."""
    # Marker names label the columns of every sample matrix in ``adata.X``.
    print("\nMarker names:")
    print(list(adata.var_names))
    # Anchor pairs preserve the batch and sample relationships used by the loader.

    # print("\nAnchor pairs:")
    # print(adata.uns["anchor_pairs"])

    # One row per batch and sample makes the inferred input structure inspectable.
    summary = pd.DataFrame(adata.obs[columns]).drop_duplicates()
    summary["sample_size"] = [
        int(
            (
                (adata.obs["batch_index"] == batch_index)
                & (adata.obs["sample_index"] == sample_index)
            ).sum()
        )
        for batch_index, sample_index in zip(
            summary["batch_index"], summary["sample_index"], strict=True
        )
    ]
    return summary.reset_index(drop=True)


def get_sample_data(
    adata: AnnData,
    batch_index: int,
    sample_index: int,
    layer: str | None = None,
) -> np.ndarray[Any, Any]:
    """from X or a layer containing all samples observations-by-markers together
    Filter one sample's observations-by-markers matrix"""
    sample_mask = (adata.obs["batch_index"] == batch_index) & (
        adata.obs["sample_index"] == sample_index
    )
    selected = adata[sample_mask.to_numpy()]
    matrix = selected.X if layer is None else selected.layers[layer]
    if matrix is None:
        raise ValueError("Selected AnnData matrix is empty.")
    return np.asarray(matrix).copy()
