"""
FastAPI dependency providers for FedSentinel.
"""

from functools import lru_cache

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from backend.auth.roles import Role
from backend.auth.routes import get_current_user
from backend.services.federation_service import FederationService
from backend.services.round_orchestrator import RoundOrchestrator
from backend.storage.models import User


# ============================================================================
# APPLICATION SERVICES
# ============================================================================

@lru_cache(maxsize=1)
def get_orchestrator() -> RoundOrchestrator:
    """
    Return the application-wide FedSentinel orchestrator.
    """

    return RoundOrchestrator()


@lru_cache(maxsize=1)
def get_federation_service() -> FederationService:
    """
    Return the application-wide federation execution service.

    The service shares the same orchestrator instance as the REST API.
    """

    return FederationService(
        orchestrator=get_orchestrator(),
    )


# ============================================================================
# AUTHENTICATION
# ============================================================================

def get_current_user_dependency(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Return the authenticated user.

    This wrapper gives other API modules a stable dependency provider.
    """

    return current_user


# ============================================================================
# ROLE AUTHORIZATION
# ============================================================================

def require_roles(*allowed_roles: Role):
    """
    Create a dependency that requires one of the supplied roles.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in {
            role.value for role in allowed_roles
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return dependency


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require SUPER_ADMIN or ADMIN.
    """

    if current_user.role not in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )

    return current_user


def require_security_analyst(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require a security analyst or higher privilege.
    """

    if current_user.role not in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
        Role.SECURITY_ANALYST.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security analyst privileges required.",
        )

    return current_user


def require_hospital_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require a hospital administrator or higher privilege.
    """

    if current_user.role not in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
        Role.HOSPITAL_ADMIN.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital administrator privileges required.",
        )

    return current_user


def require_hospital_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require a hospital user or higher privilege.
    """

    if current_user.role not in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
        Role.HOSPITAL_ADMIN.value,
        Role.HOSPITAL_OPERATOR.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital user privileges required.",
        )

    return current_user


# ============================================================================
# HOSPITAL ACCESS CONTROL
# ============================================================================

def ensure_hospital_access(
    current_user: User,
    hospital_id: str,
) -> None:
    """
    Ensure the authenticated user is allowed to access the requested hospital.

    SUPER_ADMIN and ADMIN may access any hospital.

    HOSPITAL_ADMIN and HOSPITAL_OPERATOR may only access
    their own hospital.
    """

    if current_user.role in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
    }:
        return

    if current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this hospital.",
        )


def require_hospital_access(
    current_user: User = Depends(require_hospital_user),
) -> User:
    """
    Require an authenticated hospital user associated
    with a hospital.

    SUPER_ADMIN and ADMIN are allowed through because they
    may operate across hospitals.
    """

    if current_user.role in {
        Role.HOSPITAL_ADMIN.value,
        Role.HOSPITAL_OPERATOR.value,
    }:
        if current_user.hospital_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital.",
            )

    return current_user
