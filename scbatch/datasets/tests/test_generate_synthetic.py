"""Tests for synthetic AnnData generation."""

import unittest
from typing import Any, cast

import numpy as np

from scbatch.datasets import (
    generate_synthetic_data,
    get_sample_data,
)


class TestGenerateSyntheticData(unittest.TestCase):
    def test_generation_is_reproducible_and_has_expected_shape(self) -> None:
        first = generate_synthetic_data(
            num_observations=12,
            num_variates=3,
            num_batches=3,
            num_samples_per_batch=5,
            seed=7,
        )
        second = generate_synthetic_data(
            num_observations=12,
            num_variates=3,
            num_batches=3,
            num_samples_per_batch=5,
            seed=7,
        )

        self.assertEqual(first.shape, (12 * 3 * 5, 3))
        np.testing.assert_array_equal(cast(Any, first.X), cast(Any, second.X))
        self.assertEqual(
            np.count_nonzero(first.obs["is_anchor"].to_numpy(dtype=bool)),
            12 * 4,
        )

    def test_no_batch_affect_makes_paired_samples_equal(self) -> None:
        adata = generate_synthetic_data(
            num_observations=12,
            num_variates=2,
            num_batches=3,
            num_samples_per_batch=5,
            no_batch_affect=True,
        )
        np.testing.assert_array_equal(
            get_sample_data(adata, batch_index=1, sample_index=0),
            get_sample_data(adata, batch_index=0, sample_index=0),
        )
        np.testing.assert_array_equal(
            get_sample_data(adata, batch_index=2, sample_index=0),
            get_sample_data(adata, batch_index=1, sample_index=1),
        )

    def test_generation_rejects_too_few_samples_for_intermediate_anchors(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least two samples per batch"):
            generate_synthetic_data(num_batches=3, num_samples_per_batch=1)
