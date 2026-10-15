from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status
)
from sqlalchemy.orm import Session

from dependencies.database import get_database
from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomeActionResponse,
    IncomePaginatedResponse
)
from services.income_service import (
    IncomeService,
    IncomeNotFoundError,
    InvalidIncomeOperationError
)
import os
from pathlib import Path
from uuid import uuid4

from fastapi import File, UploadFile

router = APIRouter(
    prefix="/api/income",
    tags=["Income"],
)


def get_income_service(db: Session = Depends(get_database)) -> IncomeService:
    return IncomeService(db)


IncomeServiceDependency = Annotated[IncomeService,Depends(get_income_service)]


@router.get("/",response_model=IncomePaginatedResponse)
def get_all_income(
    service: IncomeServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 5,
    income_name: Annotated[str | None,Query(min_length=1)] = None
):
    return service.get_incomes(page=page,page_size=page_size,income_name=income_name)

@router.get("/{income_id}",response_model=IncomeResponse)
def get_one_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return service.get_income(income_id)
    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/",response_model=IncomeResponse,status_code=status.HTTP_201_CREATED)
def create_income(
    data: IncomeCreate,
    service: IncomeServiceDependency,
):
    try:
        return service.create_income(data)

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

@router.put("/{income_id}",response_model=IncomeResponse)
def update_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomeUpdate,
    service: IncomeServiceDependency
):
    try:
        return service.update_income(income_id, data)

    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

@router.patch("/{income_id}",response_model=IncomeResponse)
def patch_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomePatch,
    service: IncomeServiceDependency,
):
    try:
        return service.patch_income(income_id, data)
    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

@router.delete("/{income_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        service.delete_income(income_id)
    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc



UPLOAD_DIR = Path("uploads/income")
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/{income_id}/upload")
async def upload_income_file(
    income_id: int,
    service: IncomeServiceDependency,
    file: UploadFile = File(...),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG, PNG and WEBP files are allowed.",
        )

    income = service.get_income(income_id)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 5 MB.",
            )

        with file_path.open("wb") as uploaded_file:
            uploaded_file.write(content)

        income.file_path = str(file_path).replace("\\", "/")

        service.db.commit()
        service.db.refresh(income)

        return {
            "message": "File uploaded successfully.",
            "income_id": income.income_id,
            "file_path": income.file_path,
        }

    except Exception:
        service.db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    finally:
        await file.close()
