"""Request/response shapes for the auth + users routers.

Every response is wrapped in a `data` envelope to match the rest of the API
(TDD §12); errors go through the shared handlers in core/exceptions.py.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserResponse(BaseModel):
    data: UserPublic


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    data: TokenData
