from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.api.dependencies.service_dependecies import get_auth_service
from app.models.user import User
from app.services.auth_service import (
    AuthService,
    AuthenticationError,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        return await service.get_user_from_token(payload)

    except HTTPException:
        raise
    except (
        jwt.InvalidTokenError,
        AuthenticationError,
        ValueError,
        TypeError,
        KeyError
    ):
        raise credentials_error


def require_roles(*allowed_roles: str):
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker

