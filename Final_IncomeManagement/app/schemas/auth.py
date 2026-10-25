from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_.-]+$"
    )

    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role: Literal["admin", "user"]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        min_length=20,
        max_length=4096,
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        min_length=20,
        max_length=4096,
    )


class TokenInfoResponse(BaseModel):
    user_id: int
    role: str
    token_type: str