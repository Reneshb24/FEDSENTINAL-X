"""
MNIST dataset download utilities.
"""

from pathlib import Path

from torchvision import datasets


DEFAULT_DATA_ROOT = Path("data/raw")


def download_mnist(
    root: Path | str = DEFAULT_DATA_ROOT,
) -> tuple[datasets.MNIST, datasets.MNIST]:
    """
    Download MNIST training and test datasets if they are not already
    available locally.

    Returns:
        training_dataset, test_dataset
    """

    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    train_dataset = datasets.MNIST(
        root=str(root),
        train=True,
        download=True,
    )

    test_dataset = datasets.MNIST(
        root=str(root),
        train=False,
        download=True,
    )

    return train_dataset, test_dataset


if __name__ == "__main__":
    train, test = download_mnist()

    print(f"MNIST training samples: {len(train)}")
    print(f"MNIST test samples: {len(test)}")
    print("MNIST DOWNLOAD OK")