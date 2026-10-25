import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.security import decode_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
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
        
        user = await AuthService(db).get_user_from_token(payload)
        return user

    except HTTPException:
        raise
    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        raise credentials_error from exc


def require_roles(*allowed_roles: str):
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker


def require_permissions(*required_permissions: str):
    role_permissions = {
        "admin": {
            "income:read",
            "income:create",
            "income:update",
            "income:delete",
            "expense:read",
            "expense:create",
            "expense:update",
            "expense:delete"
        },
        "user": {
            "income:read",
            "expense:read"
        },
    }

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        permissions = role_permissions.get(
            current_user.role,
            set(),
        )

        if not set(required_permissions).issubset(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return permission_checker