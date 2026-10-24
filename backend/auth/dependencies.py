"""
Authentication and authorization dependencies for FedSentinel.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from backend.auth.roles import Role
from backend.auth.security import decode_access_token
from backend.core.config import settings
from backend.storage.database import get_db
from backend.storage.models import RefreshSession
from backend.storage.models import User


bearer_scheme = HTTPBearer()


# ============================================================================
# Current authenticated user
# ============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the access token and return the authenticated user.
    """

    token = credentials.credentials

    # ------------------------------------------------------------------------
    # Decode JWT
    # ------------------------------------------------------------------------

    try:
        payload = decode_access_token(
            token,
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    # ------------------------------------------------------------------------
    # Token type
    # ------------------------------------------------------------------------

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    session_id = payload.get("sid")

    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed access token",
        )

    # ------------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # ------------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------------

    session = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.id == session_id,
            RefreshSession.user_id == user.id,
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found",
        )

    if session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
        )

    return user


# ============================================================================
# Generic role dependency
# ============================================================================

def require_roles(*allowed_roles: Role):

    def dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        allowed_values = {
            role.value
            for role in allowed_roles
        }

        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return dependency


# ============================================================================
# Common permission groups
# ============================================================================

require_admin = require_roles(
    Role.SUPER_ADMIN,
    Role.ADMIN,
)


require_security_analyst = require_roles(
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.SECURITY_ANALYST,
)


require_hospital_admin = require_roles(
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.HOSPITAL_ADMIN,
)


require_hospital_user = require_roles(
    Role.SUPER_ADMIN,
    Role.ADMIN,
    Role.HOSPITAL_ADMIN,
    Role.HOSPITAL_OPERATOR,
)


# ============================================================================
# Hospital ownership
# ============================================================================

def ensure_hospital_access(
    current_user: User,
    hospital_id: str,
) -> None:
    """
    Ensure that the authenticated user is allowed to access
    resources belonging to the specified hospital.

    SUPER_ADMIN and ADMIN have federation-wide access.

    HOSPITAL_ADMIN and HOSPITAL_OPERATOR can only access
    resources belonging to their own hospital.
    """

    # ------------------------------------------------------------------------
    # Federation administrators
    # ------------------------------------------------------------------------

    if current_user.role in {
        Role.SUPER_ADMIN.value,
        Role.ADMIN.value,
    }:
        return

    # ------------------------------------------------------------------------
    # Hospital users
    # ------------------------------------------------------------------------

    if current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this hospital",
        )


# ============================================================================
# Require hospital association
# ============================================================================

def require_hospital_access(
    current_user: User = Depends(
        require_hospital_user
    ),
) -> User:
    """
    Require an authenticated hospital-capable user.

    Hospital users must be associated with a hospital.

    Global administrators are allowed through because they are
    intentionally permitted to operate across hospitals.
    """

    if current_user.role in {
        Role.HOSPITAL_ADMIN.value,
        Role.HOSPITAL_OPERATOR.value,
    }:
        if current_user.hospital_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with a hospital",
            )

    return current_user