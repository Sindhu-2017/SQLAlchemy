from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    File, 
    UploadFile,
    Body
)
from decimal import Decimal
from sqlalchemy.orm import Session

from dependencies.database import get_database
from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomeActionResponse,
    IncomePaginatedResponse,
    IncomeFileUploadResponse
)
from services.income_service import (
    IncomeService,
    IncomeNotFoundError,
    InvalidIncomeOperationError
)

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
            detail=str(exc)
        ) from exc


@router.post("/",response_model=IncomeResponse,status_code=status.HTTP_201_CREATED)
def create_income(
    data: IncomeCreate,
    service: IncomeServiceDependency
):
    try:
        return service.create_income(data)

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
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
            detail=str(exc)
        ) from exc

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        ) from exc

@router.patch("/{income_id}",response_model=IncomeResponse)
def patch_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomePatch,
    service: IncomeServiceDependency
):
    try:
        return service.patch_income(income_id, data)
    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        ) from exc


@router.patch("/{income_id}/expense",response_model=IncomeResponse)
def update_income_expense(
    income_id: int,
    expense_amount: Decimal = Body(embed=True, ge=0),
    service: IncomeServiceDependency = None,
):
    try:
        return service.update_expense_using_procedure(income_id=income_id,expense_amount=expense_amount)
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


@router.delete("/{income_id}")
def delete_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return service.delete_income(income_id)
    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc



@router.post("/{income_id}/upload", response_model=IncomeFileUploadResponse)
async def upload_income_file(
    income_id: int,
    service: IncomeServiceDependency,
    file: UploadFile = File(...)
):
    try:
        return await service.upload_income_file(income_id=income_id,file=file)

    except IncomeNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    except InvalidIncomeOperationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
