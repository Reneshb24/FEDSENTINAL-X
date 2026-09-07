"""
FastAPI dependency providers for FedSentinel.

The API uses one in-memory RoundOrchestrator instance for the lifetime
of the application process.

The orchestrator remains the source of truth for:
    - rounds
    - incidents
    - security events

Security detection logic is NOT implemented here.
"""

from functools import lru_cache

from backend.services.round_orchestrator import RoundOrchestrator


@lru_cache(maxsize=1)
def get_orchestrator() -> RoundOrchestrator:
    """
    Return the application-wide FedSentinel orchestrator.

    A singleton is used because the current backend stores operational
    state in memory. This keeps rounds, incidents, and events consistent
    across API requests during the process lifetime.
    """

    return RoundOrchestrator()