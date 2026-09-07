"""
FedSentinel FastAPI application.

Application entry point for the FedSentinel security control plane.
"""

from fastapi import FastAPI

from backend.api.routes import router
from backend.api.websocket import router as websocket_router
from backend.core.constants import APP_NAME, APP_VERSION


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "FedSentinel — Security Control Plane for Federated AI. "
        "Evidence-driven detection, attribution, trust, quarantine, "
        "and incident management for federated model updates."
    ),
)


# ------------------------------------------------------------------
# REST API
# ------------------------------------------------------------------

app.include_router(router)


# ------------------------------------------------------------------
# WebSocket API
# ------------------------------------------------------------------

app.include_router(websocket_router)


@app.get(
    "/",
    tags=["System"],
)
def root() -> dict[str, str]:
    """
    Basic API entry-point information.
    """

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }