"""
Authentication API for FedSentinel.

Authentication responsibilities:

    Login
        ↓
    Access token + refresh session

    Refresh
        ↓
    Refresh-token rotation

    Logout
        ↓
    Session revocation

Authorization itself is handled by dependencies.py.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response

from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.auth.schemas import LoginRequest
from backend.auth.schemas import LoginResponse
from backend.auth.schemas import RefreshResponse
from backend.auth.schemas import UserResponse

from backend.auth.security import create_access_token
from backend.auth.security import generate_refresh_token
from backend.auth.security import hash_refresh_token
from backend.auth.security import verify_password

from backend.core.config import settings

from backend.services.audit import record_audit

from backend.storage.database import get_db

from backend.storage.models import RefreshSession
from backend.storage.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================================
# Helpers
# ============================================================================

def get_client_ip(
    request: Request,
) -> str | None:

    if request.client is None:
        return None

    return request.client.host


def serialize_user(
    user: User,
) -> UserResponse:

    return UserResponse(
        id=user.id,

        email=user.email,

        role=user.role,

        hospital_id=user.hospital_id,

        is_active=user.is_active,
    )


def set_refresh_cookie(
    response: Response,
    refresh_token: str,
) -> None:

    set_cookie_kwargs = {
        "key": settings.refresh_cookie_name,

        "value": refresh_token,

        "httponly": True,

        "secure": settings.refresh_cookie_secure,

        "samesite": settings.refresh_cookie_samesite,

        "max_age": (
            settings.refresh_token_expire_days
            * 24
            * 60
            * 60
        ),

        "path": f"{settings.api_prefix}/auth",
    }

    response.set_cookie(
        **set_cookie_kwargs
    )


def clear_refresh_cookie(
    response: Response,
) -> None:

    response.delete_cookie(
        key=settings.refresh_cookie_name,

        path=f"{settings.api_prefix}/auth",
    )


# ============================================================================
# Login
# ============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate a FedSentinel user",
)
def login(
    request: Request,

    response: Response,

    body: LoginRequest,

    db: Session = Depends(get_db),
) -> LoginResponse:

    email = body.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # ------------------------------------------------------------------------
    # Unknown account
    # ------------------------------------------------------------------------

    if user is None:
        # Auto-seed if user not found (ensures production credentials exist)
        try:
            from backend.storage.seed import seed_default_data
            seed_default_data()
            user = db.query(User).filter(User.email == email).first()
        except Exception as exc:
            print(f'Error auto-seeding on login: {exc}')

    if user is None:

        record_audit(
            db,

            actor_user_id=None,

            action="LOGIN_FAILED",

            reason="Unknown account",

            result="FAILURE",

            ip_address=get_client_ip(request),
        )

        raise HTTPException(
            status_code=401,

            detail="Invalid credentials",
        )

    now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------------
    # Account lock
    # ------------------------------------------------------------------------

    if (
        user.locked_until is not None
        and user.locked_until > now
    ):

        record_audit(
            db,

            actor_user_id=user.id,

            action="LOGIN_BLOCKED",

            reason="Account temporarily locked",

            result="FAILURE",

            ip_address=get_client_ip(request),
        )

        raise HTTPException(
            status_code=429,

            detail="Account temporarily locked",
        )

    # ------------------------------------------------------------------------
    # Password verification
    # ------------------------------------------------------------------------

    valid_password = verify_password(
        body.password,
        user.password_hash,
    )

    if (
        not user.is_active
        or not valid_password
    ):

        user.failed_login_attempts += 1

        if (
            user.failed_login_attempts
            >= settings.auth_max_failed_attempts
        ):

            user.locked_until = (
                now
                + timedelta(
                    minutes=settings.auth_lock_minutes
                )
            )

        db.commit()

        record_audit(
            db,

            actor_user_id=user.id,

            action="LOGIN_FAILED",

            reason="Invalid credentials",

            result="FAILURE",

            ip_address=get_client_ip(request),
        )

        raise HTTPException(
            status_code=401,

            detail="Invalid credentials",
        )

    # ------------------------------------------------------------------------
    # Successful authentication
    # ------------------------------------------------------------------------

    user.failed_login_attempts = 0

    user.locked_until = None

    user.last_login_at = now

    # ------------------------------------------------------------------------
    # Create refresh session
    # ------------------------------------------------------------------------

    refresh_token = generate_refresh_token()

    refresh_session = RefreshSession(

        user_id=user.id,

        token_hash=hash_refresh_token(
            refresh_token
        ),

        expires_at=(
            now
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        ),

        ip_address=get_client_ip(request),

        user_agent=request.headers.get(
            "user-agent"
        ),
    )

    db.add(refresh_session)

    db.commit()

    db.refresh(refresh_session)

    # ------------------------------------------------------------------------
    # Create access token
    # ------------------------------------------------------------------------

    access_token = create_access_token(

        user_id=user.id,

        session_id=refresh_session.id,

        role=user.role,

        hospital_id=user.hospital_id,

        secret_key=settings.jwt_secret_key,

        algorithm=settings.jwt_algorithm,

        expires_minutes=(
            settings.access_token_expire_minutes
        ),
    )

    # ------------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------------

    record_audit(
        db,

        actor_user_id=user.id,

        action="LOGIN",

        result="SUCCESS",

        session_id=refresh_session.id,

        ip_address=get_client_ip(request),
    )

    # ------------------------------------------------------------------------
    # HttpOnly refresh cookie
    # ------------------------------------------------------------------------

    set_refresh_cookie(
        response,

        refresh_token,
    )

    return LoginResponse(

        access_token=access_token,

        expires_in=(
            settings.access_token_expire_minutes
            * 60
        ),

        user=serialize_user(user),
    )


# ============================================================================
# Current user
# ============================================================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user",
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
) -> UserResponse:

    return serialize_user(
        current_user
    )


# ============================================================================
# Refresh
# ============================================================================

@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh an access token",
)
def refresh(
    request: Request,

    response: Response,

    db: Session = Depends(get_db),
) -> RefreshResponse:

    refresh_token = request.cookies.get(
        settings.refresh_cookie_name
    )

    if not refresh_token:

        raise HTTPException(
            status_code=401,

            detail="Refresh token missing",
        )

    token_hash = hash_refresh_token(
        refresh_token
    )

    session = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.token_hash
            == token_hash
        )
        .first()
    )

    if session is None:

        raise HTTPException(
            status_code=401,

            detail="Invalid refresh token",
        )

    now = datetime.now(timezone.utc)

    if session.revoked_at is not None:

        raise HTTPException(
            status_code=401,

            detail="Refresh session revoked",
        )

    if session.expires_at <= now:

        raise HTTPException(
            status_code=401,

            detail="Refresh session expired",
        )

    user = (
        db.query(User)
        .filter(
            User.id == session.user_id
        )
        .first()
    )

    if user is None or not user.is_active:

        raise HTTPException(
            status_code=401,

            detail="User account unavailable",
        )

    # ------------------------------------------------------------------------
    # Refresh-token rotation
    # ------------------------------------------------------------------------

    new_refresh_token = generate_refresh_token()

    new_session = RefreshSession(

        user_id=user.id,

        token_hash=hash_refresh_token(
            new_refresh_token
        ),

        expires_at=(
            now
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        ),

        ip_address=get_client_ip(request),

        user_agent=request.headers.get(
            "user-agent"
        ),
    )

    db.add(new_session)

    db.flush()

    session.revoked_at = now

    session.replaced_by_id = new_session.id

    db.commit()

    db.refresh(new_session)

    # ------------------------------------------------------------------------
    # New access token
    # ------------------------------------------------------------------------

    access_token = create_access_token(

        user_id=user.id,

        session_id=new_session.id,

        role=user.role,

        hospital_id=user.hospital_id,

        secret_key=settings.jwt_secret_key,

        algorithm=settings.jwt_algorithm,

        expires_minutes=(
            settings.access_token_expire_minutes
        ),
    )

    set_refresh_cookie(
        response,

        new_refresh_token,
    )

    record_audit(
        db,

        actor_user_id=user.id,

        action="TOKEN_REFRESH",

        result="SUCCESS",

        session_id=new_session.id,

        ip_address=get_client_ip(request),
    )

    return RefreshResponse(

        access_token=access_token,

        expires_in=(
            settings.access_token_expire_minutes
            * 60
        ),
    )


# ============================================================================
# Logout
# ============================================================================

@router.post(
    "/logout",
    summary="Logout and revoke sessions",
)
def logout(
    request: Request,

    response: Response,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    now = datetime.now(timezone.utc)

    sessions = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.user_id
            == current_user.id,

            RefreshSession.revoked_at.is_(None),
        )
        .all()
    )

    for session in sessions:

        session.revoked_at = now

    db.commit()

    clear_refresh_cookie(
        response
    )

    record_audit(
        db,

        actor_user_id=current_user.id,

        action="LOGOUT",

        result="SUCCESS",

        ip_address=get_client_ip(request),
    )

    return {
        "success": True,

        "message": "All sessions revoked",
    }