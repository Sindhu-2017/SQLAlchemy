from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.auth import get_current_user
from app.dependencies.service_dependecies import get_auth_service
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenInfoResponse,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    AuthService,
    AuthenticationError,
    RegistrationConflict,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

AuthServiceDependency = Annotated[
    AuthService,
    Depends(get_auth_service),
]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    service: AuthServiceDependency,
) -> User:
    try:
        return await service.register(data)

    except RegistrationConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    service: AuthServiceDependency,
) -> dict[str, str]:
    try:
        return await service.login(
            username=form_data.username,
            password=form_data.password,
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshRequest,
    service: AuthServiceDependency,
) -> dict[str, str]:
    try:
        return await service.refresh(data.refresh_token)

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: LogoutRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    service: AuthServiceDependency,
) -> Response:
    try:
        await service.logout(
            raw_refresh_token=data.refresh_token,
            current_user_id=current_user.user_id,
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    return current_user


@router.get(
    "/token-info",
    response_model=TokenInfoResponse,
)
async def get_token_info(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> TokenInfoResponse:
    return TokenInfoResponse(
        user_id=current_user.user_id,
        role=current_user.role,
        token_type="access",
    )