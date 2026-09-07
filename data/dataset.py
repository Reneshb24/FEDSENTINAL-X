"""
Dataset utilities for FedSentinel federated clients.
"""

from pathlib import Path
from typing import Sequence

import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms


DEFAULT_DATA_ROOT = Path("data/raw")


def get_mnist_transform() -> transforms.Compose:
    """Return the preprocessing pipeline shared by all clients."""

    return transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.1307,),
                std=(0.3081,),
            ),
        ]
    )


def load_mnist_train(
    root: Path | str = DEFAULT_DATA_ROOT,
) -> datasets.MNIST:
    """Load the MNIST training dataset."""

    return datasets.MNIST(
        root=str(root),
        train=True,
        download=False,
        transform=get_mnist_transform(),
    )


def load_mnist_test(
    root: Path | str = DEFAULT_DATA_ROOT,
) -> datasets.MNIST:
    """Load the MNIST test dataset."""

    return datasets.MNIST(
        root=str(root),
        train=False,
        download=False,
        transform=get_mnist_transform(),
    )


def create_client_subset(
    dataset: Dataset,
    indices: Sequence[int],
) -> Subset:
    """Create a dataset subset for one federated client."""

    if not indices:
        raise ValueError("Client dataset cannot be empty.")

    return Subset(dataset, list(indices))


def create_client_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
) -> DataLoader:
    """Create a DataLoader for local client training."""

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        pin_memory=False,
    )


def get_targets(dataset: Dataset) -> torch.Tensor:
    """
    Return labels from a dataset.

    Supports the standard MNIST dataset and Subset instances.
    """

    if isinstance(dataset, Subset):
        parent_targets = get_targets(dataset.dataset)
        indices = torch.tensor(dataset.indices, dtype=torch.long)
        return parent_targets[indices]

    if hasattr(dataset, "targets"):
        targets = dataset.targets

        if isinstance(targets, torch.Tensor):
            return targets.detach().cpu()

        return torch.as_tensor(targets, dtype=torch.long)

    raise TypeError(
        "Dataset must expose a 'targets' attribute or be a torch Subset."
    )