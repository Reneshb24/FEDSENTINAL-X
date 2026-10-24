"""
FedSentinel FastAPI application.

Application entry point for the FedSentinel security control plane.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.api.websocket import router as websocket_router
from backend.api.hospital_portal_routes import (
    router as hospital_portal_router,
)
from backend.api.hospital_dataset_routes import (
    router as hospital_dataset_router,
)
from backend.api.audit_routes import router as audit_router

from backend.auth.routes import router as auth_router

from backend.core.config import settings
from backend.core.constants import APP_NAME, APP_VERSION

from backend.storage.database import init_database


# ============================================================================
# Application lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    # ------------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------------

    init_database()

    yield

    # ------------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------------

    # Future cleanup can be placed here.


# ============================================================================
# FastAPI application
# ============================================================================

app = FastAPI(
    title=APP_NAME,

    version=APP_VERSION,

    description=(
        "FedSentinel — Security Control Plane for Federated AI. "
        "Evidence-driven detection, attribution, trust, quarantine, "
        "and incident management for federated model updates."
    ),

    lifespan=lifespan,
)


# ============================================================================
# CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.onrender\.com)(:\d+)?$",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================================
# Existing FedSentinel REST API
# ============================================================================
#
# This router already contains:
#   - Core FedSentinel routes
#   - Hospital management routes
#   - Federation routes
#   - Security investigation routes
#
# Therefore those routers must NOT be registered separately here.
# ============================================================================

app.include_router(router)


# ============================================================================
# Hospital Portal API
# ============================================================================

app.include_router(
    hospital_portal_router,
    prefix="/api/v1",
)

app.include_router(
    hospital_dataset_router,
    prefix="/api/v1",
)


# ============================================================================
# Audit API
# ============================================================================

app.include_router(
    audit_router,
    prefix="/api/v1",
)


# ============================================================================
# Authentication API
# ============================================================================

app.include_router(
    auth_router,
    prefix=settings.api_prefix,
)


# ============================================================================
# Existing WebSocket API
# ============================================================================

app.include_router(
    websocket_router
)


# ============================================================================
# Root
# ============================================================================

@app.get(
    "/",
    tags=["System"],
)
def root() -> dict[str, object]:
    """
    Basic API entry-point information and database seeding verification.
    """
    from backend.storage.database import SessionLocal
    from backend.storage.models import User
    from backend.storage.seed import seed_default_data

    user_count = 0
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            seed_default_data()
            user_count = db.query(User).count()
    except Exception as exc:
        print(f"Error checking users: {exc}")
    finally:
        db.close()

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "users": user_count,
    }