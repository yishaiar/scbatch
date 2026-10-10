"""Generate synthetic batched samples as AnnData."""

from pathlib import Path
from typing import Any

import numpy as np
from anndata import AnnData

from .create_adata import create_adata_from_dataset
from .utils import save_adata_to_json, summarize_samples


def generate_synthetic_data(
    num_observations: int = 10000,
    num_variates: int = 4,
    num_batches: int = 3,
    num_samples_per_batch: int = 5,
    seed: int = 42,
    no_batch_affect: bool = False,
) -> AnnData:
    """Generate synthetic samples and return them as an annotated AnnData.

    Adjacent batches share biological samples, with each batch's technical
    baseline applied separately. The generated matrices and anchor indexes are
    passed to ``create_adata_from_dataset`` to build the returned object.

    Args:
        num_observations: Number of rows in each sample matrix.
        num_variates: Number of features in each sample matrix.
        num_batches: Number of batches to generate.
        num_samples_per_batch: Number of sample matrices in each batch.
        seed: Seed for reproducible random samples.
        no_batch_affect: If true, generate zero technical baselines.

    Returns:
        An AnnData containing all generated observations, markers, batch and
        sample metadata, and anchor metadata.
    """
    if num_observations < 1 or num_variates < 1 or num_batches < 1 or num_samples_per_batch < 1:
        raise ValueError(
            "num_observations, num_variates, num_batches, and "
            "num_samples_per_batch must be positive."
        )
    if num_batches > 2 and num_samples_per_batch < 2:
        raise ValueError("At least two samples per batch are needed for three or more batches.")

    baselines = _generate_batch_effect_baselines(
        num_samples=num_observations,
        num_variates=num_variates,
        num_batches=num_batches,
        seed=seed,
    )
    dataset = _create_batch_dataset(
        baselines,
        num_samples_per_batch,
        seed,
        no_batch_affect,
    )
    anchor_pairs = _invert_anchor_pairs(_select_anchors(dataset))
    return create_adata_from_dataset(dataset, anchor_pairs)


def _generate_batch_effect_baselines(
    num_samples: int = 1000,
    num_variates: int = 4,
    num_batches: int = 3,
    seed: int = 42,
    print_: bool = False,
) -> list[np.ndarray[Any, Any]]:
    """Generate a technical baseline matrix for each batch.

    Each baseline has ``num_samples`` rows and ``num_variates`` columns.
    The mean and standard deviation increase across batches.
    """
    np.random.seed(seed)
    baselines = []
    mean = 0.5
    std = 0.3
    for batch_index in range(num_batches):
        mean = mean + np.random.uniform(1.0, 2.0, num_variates)
        std = std * np.random.uniform(1.1, 1.3, num_variates)
        baseline = np.random.normal(loc=mean, scale=std, size=(num_samples, num_variates))
        baselines.append(baseline)
        if print_:
            print(f"Batch Affect Distribution Batch_{batch_index} - {num_variates} variates")
            print(f"std: {std}")
            print(f"mu: {mean}")
    return baselines


def _select_anchors(
    dataset: list[list[np.ndarray[Any, Any]]] | list[list[np.ndarray[Any, Any] | None]],
) -> list[dict[str, int]]:
    """Choose sample indexes to act as anchors between consecutive batches.

    Since these are synthetic data, this function designates which generated
    samples should share the same biological signal. The first pair uses
    sample 0 in both batches; later pairs use sample 1 in the source batch and
    sample 0 in the next batch.
    """
    return [
        {
            "from_batch": batch_index,
            "from_sample": 0 if batch_index == 0 else 1,
            "to_batch": batch_index + 1,
            "to_sample": 0,
        }
        for batch_index in range(len(dataset) - 1)
    ]


def _create_batch_dataset(
    batch_effect_baselines: list[np.ndarray[Any, Any]],
    num_batch_samples: int = 5,
    seed: int = 42,
    no_batch_affect: bool = False,
) -> list[list[np.ndarray[Any, Any]]]:
    """Create samples in each batch by adding biological signal to baselines.

    Each pair of consecutive batches receives one shared biological sample.
    Other sample slots receive independent biological samples. When
    ``no_batch_affect`` is true, baselines are zeroed before samples are built.
    """
    np.random.seed(seed)
    num_variates = batch_effect_baselines[0].shape[1]
    num_observations = batch_effect_baselines[0].shape[0]
    if no_batch_affect:
        batch_effect_baselines = [np.zeros_like(baseline) for baseline in batch_effect_baselines]

    dataset: list[list[np.ndarray[Any, Any] | None]] = [
        [None] * num_batch_samples for _ in batch_effect_baselines
    ]
    anchor_pairs = _select_anchors(dataset)
    for pair in anchor_pairs:
        mean = np.random.uniform(1.0, 2.0, num_variates)
        std = np.random.uniform(0.4, 0.6, num_variates)
        biological_sample = _generate_bimodal_sample(
            num_samples=num_observations,
            num_variates=num_variates,
            mu=mean,
            std=std,
        )
        source = pair["from_batch"], pair["from_sample"]
        target = pair["to_batch"], pair["to_sample"]
        dataset[source[0]][source[1]] = batch_effect_baselines[source[0]] + biological_sample
        dataset[target[0]][target[1]] = batch_effect_baselines[target[0]] + biological_sample

    for batch_index, samples in enumerate(dataset):
        non_anchor_index = 0
        for sample_index, sample in enumerate(samples):
            if sample is not None:
                continue
            scale = 2.0 if non_anchor_index == 3 else 1.0
            mean = np.random.uniform(1.0 * scale, 2.0 * scale, num_variates)
            std = np.random.uniform(0.4 * scale, 0.6 * scale, num_variates)
            biological_sample = _generate_bimodal_sample(
                num_samples=num_observations,
                num_variates=num_variates,
                mu=mean,
                std=std,
            )
            samples[sample_index] = batch_effect_baselines[batch_index] + biological_sample
            non_anchor_index += 1

    return [[sample for sample in samples if sample is not None] for samples in dataset]


def _generate_bimodal_sample(
    num_samples: int = 100,
    num_variates: int = 4,
    seed: int = 42,
    mu: np.ndarray[Any, Any] = np.array([1.0, 1.5, 1.2, 1.8]),
    std: np.ndarray[Any, Any] = np.array([0.4, 0.5, 0.3, 0.6]),
) -> np.ndarray[Any, Any]:
    """Generate a sample matrix from two symmetric peaks per variate.

    For each observation and variate, choose a peak centered at ``-mu`` or
    ``mu`` with standard deviation ``std``.
    """
    np.random.seed(seed)
    data = np.zeros((num_samples, num_variates))
    for column in range(num_variates):
        choose_negative_peak = np.random.rand(num_samples) < 0.5
        negative_peak = np.random.normal(-mu[column], std[column], size=num_samples)
        positive_peak = np.random.normal(mu[column], std[column], size=num_samples)
        data[:, column] = np.where(choose_negative_peak, negative_peak, positive_peak)
    return data


def _invert_anchor_pairs(
    anchor_pairs: list[dict[str, int]], target_batch: int = 1
) -> list[dict[str, int]]:
    """Reverse anchor direction so the target batch is the destination.

    Pairs not connected to ``target_batch`` retain their original direction.
    The input list and its dictionaries are left unchanged.
    """
    inverted_pairs = []
    for pair in anchor_pairs:
        inverted = pair.copy()
        if inverted["from_batch"] == target_batch and inverted["to_batch"] != target_batch:
            inverted["from_batch"], inverted["to_batch"] = (
                inverted["to_batch"],
                inverted["from_batch"],
            )
            inverted["from_sample"], inverted["to_sample"] = (
                inverted["to_sample"],
                inverted["from_sample"],
            )
        inverted_pairs.append(inverted)
    return inverted_pairs


def _print_dataset_info(
    dataset: list[list[np.ndarray[Any, Any]]], anchor_pairs: list[dict[str, int]]
) -> None:
    """Print each batch's dimensions and the sample indexes in each anchor.

    This is a console summary for inspecting a generated nested-list dataset.
    """
    print(f"Number of batches: {len(dataset)}")
    for batch_index, samples in enumerate(dataset):
        print(
            f"  Batch_{batch_index}: {len(samples)} samples, "
            f"each with {samples[0].shape[1]} variates and "
            f"{samples[0].shape[0]} data points"
        )
    print("\nAnchor pairs:")
    for pair in anchor_pairs:
        print(
            f"  Batch {pair['from_batch']} (Sample {pair['from_sample']}) -> "
            f"Batch {pair['to_batch']} (Sample {pair['to_sample']})"
        )


if __name__ == "__main__":
    synthetic_adata = generate_synthetic_data(num_observations=10)
    fixture_path = Path(__file__).parent / "synthetic" / "test_dataset.json"

    print(summarize_samples(synthetic_adata))
    print(synthetic_adata)

    save_adata_to_json(synthetic_adata, fixture_path)
