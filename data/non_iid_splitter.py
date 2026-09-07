from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
from torch.utils.data import Dataset

from data.dataset import get_targets


@dataclass(frozen=True)
class ClientPartition:
    """
    Dataset partition assigned to one federated client.

    client_id:
        Unique hospital/client identifier.

    indices:
        Indices into the original MNIST dataset.

    class_counts:
        Number of samples from each digit class.
    """

    client_id: str
    indices: List[int]
    class_counts: Dict[int, int]

    @property
    def num_samples(self) -> int:
        return len(self.indices)


def _validate_inputs(
    num_clients: int,
    seed: int,
    min_samples_per_client: int,
) -> None:
    if num_clients < 2:
        raise ValueError("num_clients must be at least 2.")

    if min_samples_per_client < 1:
        raise ValueError("min_samples_per_client must be positive.")

    if seed < 0:
        raise ValueError("seed must be non-negative.")


def create_non_iid_partitions(
    dataset: Dataset,
    num_clients: int = 20,
    seed: int = 42,
    concentration: float = 0.5,
    min_samples_per_client: int = 100,
) -> Dict[str, ClientPartition]:
    """
    Create deterministic non-IID client partitions using a Dirichlet
    distribution over class proportions.

    Each client receives a different mixture of MNIST digit classes.

    A lower concentration produces stronger non-IID behavior.
    A higher concentration produces distributions closer to IID.

    Args:
        dataset:
            MNIST training dataset.

        num_clients:
            Number of federated clients/hospitals.

        seed:
            Random seed for reproducibility.

        concentration:
            Dirichlet concentration parameter.

        min_samples_per_client:
            Minimum number of samples each client should receive.

    Returns:
        Dictionary mapping client IDs such as H1, H2, ..., H20
        to ClientPartition objects.
    """

    _validate_inputs(
        num_clients=num_clients,
        seed=seed,
        min_samples_per_client=min_samples_per_client,
    )

    if concentration <= 0:
        raise ValueError("concentration must be positive.")

    targets = np.asarray(get_targets(dataset), dtype=np.int64)

    if targets.size == 0:
        raise ValueError("Dataset must not be empty.")

    classes = np.unique(targets)

    if len(classes) < 2:
        raise ValueError("Dataset must contain at least two classes.")

    rng = np.random.default_rng(seed)

    # Store indices belonging to each class.
    class_indices = {
        int(label): np.where(targets == label)[0].tolist()
        for label in classes
    }

    # Shuffle each class independently.
    for indices in class_indices.values():
        rng.shuffle(indices)

    client_indices: Dict[str, List[int]] = {
        f"H{i + 1}": []
        for i in range(num_clients)
    }

    # Allocate each class according to a Dirichlet-distributed
    # client preference vector.
    for label in classes:
        label = int(label)
        indices = class_indices[label]

        proportions = rng.dirichlet(
            np.full(num_clients, concentration)
        )

        # Convert proportions to integer sample counts.
        raw_counts = proportions * len(indices)
        counts = np.floor(raw_counts).astype(int)

        # Distribute remaining samples according to largest remainders.
        remainder = len(indices) - int(counts.sum())

        if remainder > 0:
            fractional = raw_counts - counts
            order = np.argsort(-fractional)

            for client_position in order[:remainder]:
                counts[client_position] += 1

        cursor = 0

        for client_position, count in enumerate(counts):
            if count <= 0:
                continue

            client_id = f"H{client_position + 1}"

            selected = indices[cursor : cursor + count]
            client_indices[client_id].extend(selected)

            cursor += count

    # Make the final order deterministic but shuffled.
    for client_id in client_indices:
        rng.shuffle(client_indices[client_id])

    # Check minimum client size.
    small_clients = [
        client_id
        for client_id, indices in client_indices.items()
        if len(indices) < min_samples_per_client
    ]

    if small_clients:
        raise ValueError(
            "Non-IID partition produced clients below the minimum "
            f"sample requirement: {small_clients}"
        )

    partitions: Dict[str, ClientPartition] = {}

    for client_id, indices in client_indices.items():
        labels_for_client = targets[indices]

        class_counts = {
            int(label): int(np.sum(labels_for_client == label))
            for label in classes
            if np.any(labels_for_client == label)
        }

        partitions[client_id] = ClientPartition(
            client_id=client_id,
            indices=[int(index) for index in indices],
            class_counts=class_counts,
        )

    # Final integrity check: every dataset sample must appear exactly once.
    all_indices = [
        index
        for partition in partitions.values()
        for index in partition.indices
    ]

    if len(all_indices) != len(set(all_indices)):
        raise RuntimeError(
            "Partitioning error: duplicate dataset indices detected."
        )

    if len(all_indices) != len(dataset):
        raise RuntimeError(
            "Partitioning error: not every dataset sample was assigned."
        )

    return partitions


def summarize_partitions(
    partitions: Dict[str, ClientPartition],
) -> Dict[str, dict]:
    """
    Produce a lightweight summary suitable for logging or API responses.
    """

    return {
        client_id: {
            "num_samples": partition.num_samples,
            "class_counts": dict(partition.class_counts),
        }
        for client_id, partition in partitions.items()
    }


def save_partition_summary(
    partitions: Dict[str, ClientPartition],
    output_path: Path,
) -> None:
    """
    Save a human-readable partition summary.

    This stores metadata only, not image data.
    """

    import json

    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_partitions(partitions)

    output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    from data.dataset import load_mnist_train

    train_dataset = load_mnist_train()

    partitions = create_non_iid_partitions(
        dataset=train_dataset,
        num_clients=20,
        seed=42,
        concentration=0.5,
        min_samples_per_client=100,
    )

    print(f"Clients created: {len(partitions)}")
    print(f"Total samples: {sum(p.num_samples for p in partitions.values())}")

    for client_id, partition in partitions.items():
        print(
            f"{client_id}: "
            f"{partition.num_samples} samples | "
            f"{partition.class_counts}"
        )

    print("NON-IID PARTITIONING OK")