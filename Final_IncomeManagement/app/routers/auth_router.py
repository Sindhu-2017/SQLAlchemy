from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import (
    get_current_user,
)
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenInfoResponse,
    TokenResponse,
    UserResponse,
)
from app.security import decode_token
from app.services.auth_service import (
    AuthService,
    AuthenticationError,
    RegistrationConflict,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    try:
        return await AuthService(db).register(data)

    except RegistrationConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TokenResponse:
    try:
        tokens = await AuthService(db).login(
            username=form_data.username,
            password=form_data.password,
        )
        return TokenResponse(**tokens)

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc


@router.post(
    "/refresh",
    response_model=TokenResponse
)
async def refresh_token(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    try:
        tokens = await AuthService(db).refresh(
            data.refresh_token
        )
        return TokenResponse(**tokens)

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        ) from exc


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: LogoutRequest,
    current_user: Annotated[User,Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Response:

    try:
        await AuthService(db).logout(
            raw_refresh_token=data.refresh_token,
            user_id=current_user.user_id,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: Annotated[User,Depends(get_current_user)]
) -> User:
    return current_user


@router.get(
    "/token-info",
    response_model=TokenInfoResponse
)
async def get_token_info(
    current_user: Annotated[User,Depends(get_current_user)]
) -> TokenInfoResponse:
    return TokenInfoResponse(
        user_id=current_user.user_id,
        role=current_user.role,
        token_type="access"
    )