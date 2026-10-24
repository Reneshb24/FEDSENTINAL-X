"""
Pydantic schemas used by the authentication API.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login credentials."""

    email: str

    password: str


class UserResponse(BaseModel):
    """Public representation of an authenticated user."""

    id: str

    email: str

    role: str

    hospital_id: str | None

    is_active: bool


class LoginResponse(BaseModel):
    """Response returned after successful authentication."""

    access_token: str

    token_type: str = "bearer"

    expires_in: int

    user: UserResponse


class RefreshResponse(BaseModel):
    """Response returned after refreshing an access token."""

    access_token: str

    token_type: str = "bearer"

    expires_in: int