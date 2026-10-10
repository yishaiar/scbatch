"""Built-in demonstration dataset entrypoint."""

import json
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from anndata import AnnData

from .create_adata import create_adata_from_dataset
from .utils import summarize_samples

DemoDataset = Literal["synthetic", "cytof"]

_DEMO_FIXTURES: dict[DemoDataset, str] = {
    "synthetic": "synthetic/test_dataset.json",
    "cytof": "cytof/test_dataset.json",
}


def load_demo(dataset_name: DemoDataset = "synthetic") -> AnnData:
    """Load the synthetic or CYTOF demonstration dataset.

    The synthetic fixture stores AnnData JSON. The CYTOF fixture stores batches,
    samples, and marker names, plus anchor pairs that reference samples by their
    zero-based batch and sample indexes.

    """
    fixture_path = Path(__file__).parent / _DEMO_FIXTURES[dataset_name]
    print(f"loading {_DEMO_FIXTURES[dataset_name]}")
    payload = json.loads(fixture_path.read_text())
    if payload.get("format") == "scbatch.adata.v1":
        obs_data = payload["obs"]
        var_data = payload["var"]
        obs = pd.DataFrame(
            obs_data["data"],
            columns=obs_data["columns"],
            index=obs_data["index"],
        )
        var = pd.DataFrame(
            var_data["data"],
            columns=var_data["columns"],
            index=payload["marker_names"],
        )
        adata = AnnData(X=np.asarray(payload["X"], dtype=float), obs=obs, var=var)
    else:
        dataset = [
            [pd.DataFrame(sample, columns=payload["marker_names"], dtype=float) for sample in batch]
            for batch in payload["dataset"]
        ]
        adata = create_adata_from_dataset(dataset, payload["anchor_pairs"])
    return adata


if __name__ == "__main__":
    # demo_adata = load_demo(dataset_name="cytof")
    demo_adata = load_demo()
    print(summarize_samples(demo_adata))
    print(demo_adata)
