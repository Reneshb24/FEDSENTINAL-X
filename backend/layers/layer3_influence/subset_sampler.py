"""
FedSentinel Layer 3 validation subset sampling.

The influence layer should use a fixed validation subset so that
with-client and without-client evaluations are directly comparable.
"""

from __future__ import annotations

from torch.utils.data import DataLoader, Dataset, Subset


def create_validation_subset(
    dataset: Dataset,
    sample_size: int = 1000,
    seed: int = 42,
) -> Subset:
    """
    Create a deterministic validation subset.

    Args:
        dataset:
            Validation dataset.

        sample_size:
            Maximum number of examples to use.

        seed:
            Random seed for deterministic selection.
    """

    if dataset is None:
        raise ValueError(
            "dataset must not be None."
        )

    if len(dataset) == 0:
        raise ValueError(
            "dataset must not be empty."
        )

    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than zero."
        )

    sample_size = min(
        sample_size,
        len(dataset),
    )

    generator = __import__(
        "torch"
    ).Generator()

    generator.manual_seed(seed)

    indices = __import__(
        "torch"
    ).randperm(
        len(dataset),
        generator=generator,
    )[:sample_size].tolist()

    return Subset(
        dataset,
        indices,
    )


def create_validation_loader(
    dataset: Dataset,
    sample_size: int = 1000,
    batch_size: int = 64,
    seed: int = 42,
) -> DataLoader:
    """
    Create a deterministic validation DataLoader.
    """

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than zero."
        )

    subset = create_validation_subset(
        dataset=dataset,
        sample_size=sample_size,
        seed=seed,
    )

    return DataLoader(
        subset,
        batch_size=batch_size,
        shuffle=False,
    )