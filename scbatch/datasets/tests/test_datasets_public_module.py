"""Public namespace tests for datasets."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import scbatch
from scbatch.datasets import (
    create_adata_from_dataset,
    get_sample_data,
    load_demo,
    save_adata_to_json,
    summarize_samples,
)


class TestDatasetsNamespace(unittest.TestCase):
    def test_save_adata_to_json_writes_matrix_and_marker_names(self) -> None:
        sample = pd.DataFrame([[1.0, 2.0]], columns=pd.Index(["CD3", "CD4"]))
        adata = create_adata_from_dataset([[sample]], [])

        with tempfile.TemporaryDirectory() as temp_directory:
            fixture_path = Path(temp_directory) / "adata.json"
            save_adata_to_json(adata, fixture_path)
            payload = json.loads(fixture_path.read_text())

        self.assertEqual(payload["format"], "scbatch.adata.v1")
        self.assertEqual(payload["marker_names"], ["CD3", "CD4"])
        self.assertEqual(payload["X"], [[1.0, 2.0]])

    def test_save_adata_to_json_rejects_unserialized_layers(self) -> None:
        adata = create_adata_from_dataset([[np.ones((1, 2))]], [])
        adata.layers["extra"] = np.ones((1, 2))

        with tempfile.TemporaryDirectory() as temp_directory:
            fixture_path = Path(temp_directory) / "adata.json"
            with self.assertRaisesRegex(ValueError, "only X, obs, and var"):
                save_adata_to_json(adata, fixture_path)

    def test_demo_loader_supports_default_and_named_datasets(self) -> None:
        default_adata = load_demo()
        synthetic_adata = load_demo("synthetic")
        cytof_adata = load_demo("cytof")

        self.assertEqual(default_adata.n_vars, 4)
        self.assertListEqual(
            list(default_adata.var_names),
            ["marker_1", "marker_2", "marker_3", "marker_4"],
        )
        self.assertEqual(default_adata.obs["batch_index"].nunique(), 3)
        self.assertListEqual(default_adata.obs.index[:3].tolist(), ["0", "1", "2"])
        self.assertTrue(default_adata.obs.equals(synthetic_adata.obs))
        self.assertGreater(cytof_adata.n_obs, 0)
        self.assertGreater(cytof_adata.n_vars, 0)

        datasets_path = Path(scbatch.datasets.__file__).parent
        synthetic_fixture = datasets_path / "synthetic" / "test_dataset.json"
        cytof_fixture = datasets_path / "cytof" / "test_dataset.json"
        self.assertNotEqual(synthetic_fixture.parent, cytof_fixture.parent)
        synthetic_payload = json.loads(synthetic_fixture.read_text())
        cytof_payload = json.loads(cytof_fixture.read_text())
        self.assertEqual(synthetic_payload["format"], "scbatch.adata.v1")
        self.assertIn("dataset", cytof_payload)

    def test_summarize_samples_includes_each_sample_size(self) -> None:
        adata = create_adata_from_dataset([[np.ones((2, 2)), np.ones((3, 2))]], [])
        summary = summarize_samples(adata)
        self.assertListEqual(summary["sample_size"].tolist(), [2, 3])
        self.assertListEqual(summary.index.tolist(), [0, 1])

    def test_create_adata_from_dynamic_batched_samples(self) -> None:
        dataset = [
            [np.full((10, 3), value) for value in range(5)],
            [np.full((10, 3), value) for value in range(5, 10)],
        ]
        adata = create_adata_from_dataset(
            dataset,
            [{"from_batch": 0, "from_sample": 0, "to_batch": 1, "to_sample": 0}],
        )
        self.assertEqual(adata.shape, (100, 3))
        self.assertListEqual(list(adata.var_names), ["marker_1", "marker_2", "marker_3"])
        self.assertEqual(adata.obs["sample_id"].nunique(), 10)
        self.assertEqual(int(adata.obs["is_anchor"].sum()), 20)
        self.assertEqual(adata.obs.iloc[0]["anchor_to_batch"], "Batch_1")

    def test_create_adata_uses_dataframe_columns_as_marker_names(self) -> None:
        sample = pd.DataFrame([[1.0, 2.0]], columns=pd.Index(["CD3", "CD4"]))

        adata = create_adata_from_dataset([[sample]], [])

        self.assertListEqual(list(adata.var_names), ["CD3", "CD4"])

    def test_get_sample_data_returns_dense_data_for_input_indexes(self) -> None:
        adata = create_adata_from_dataset(
            [[np.ones((2, 2)), np.full((3, 2), 2.0)]],
            [],
        )
        sample_data = get_sample_data(adata, batch_index=0, sample_index=1)
        self.assertEqual(sample_data.shape, (3, 2))
        np.testing.assert_array_equal(sample_data, np.full((3, 2), 2.0))

    def test_create_adata_allows_dynamic_observation_counts(self) -> None:
        adata = create_adata_from_dataset(
            [[np.ones((2, 4)), np.ones((3, 4))], [np.ones((1, 4))]],
            [],
        )
        self.assertEqual(adata.shape, (6, 4))

    def test_create_adata_rejects_empty_dataset(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one batch"):
            create_adata_from_dataset([], [])

    def test_create_adata_rejects_invalid_anchor_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside dataset bounds"):
            create_adata_from_dataset(
                [[np.ones((2, 2))]],
                [{"from_batch": 0, "from_sample": 0, "to_batch": 1, "to_sample": 0}],
            )

    def test_create_adata_rejects_repeated_anchor_sample(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one anchor pair"):
            create_adata_from_dataset(
                [[np.ones((2, 2)), np.ones((2, 2))]],
                [
                    {"from_batch": 0, "from_sample": 0, "to_batch": 0, "to_sample": 1},
                    {"from_batch": 0, "from_sample": 0, "to_batch": 0, "to_sample": 1},
                ],
            )
