"""
FedSentinel lightweight CNN model.

The same architecture is used by the simulated federated clients and
the central server so their model parameters remain compatible.
"""

from torch import Tensor, nn


class FedSentinelCNN(nn.Module):
    """
    Lightweight CNN for MNIST classification.

    Input:
        [batch, 1, 28, 28]

    Output:
        [batch, 10]
    """

    def __init__(self, num_classes: int = 10) -> None:
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=16,
                kernel_size=3,
                padding=1,
            ),
            nn.ReLU(),

            nn.MaxPool2d(kernel_size=2),

            nn.Conv2d(
                in_channels=16,
                out_channels=32,
                kernel_size=3,
                padding=1,
            ),
            nn.ReLU(),

            nn.MaxPool2d(kernel_size=2),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),

            nn.Linear(
                in_features=32 * 7 * 7,
                out_features=64,
            ),
            nn.ReLU(),

            nn.Linear(
                in_features=64,
                out_features=num_classes,
            ),
        )

    def forward(self, x: Tensor) -> Tensor:
        """Run a forward pass through the network."""

        x = self.features(x)
        return self.classifier(x)