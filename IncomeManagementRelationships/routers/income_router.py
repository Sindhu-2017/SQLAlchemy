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
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.income_service import IncomeService
from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomePaginatedResponse
)

from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomeActionResponse,
    IncomePaginatedResponse
)

from exceptions.income_exceptions import(
    InvalidIncomeOperationError,
    IncomeNotFoundError
)

router = APIRouter(
    prefix = "/api/income",
    tags = ["Income"]
)

def get_income_service(db: Session = Depends(get_db)) -> IncomeService:
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
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 


@router.post("/",response_model=IncomeResponse,status_code=status.HTTP_201_CREATED)
def create_income(
    data: IncomeCreate,
    service: IncomeServiceDependency
):
    try:
        return service.create_income(data)

    except InvalidIncomeOperationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

@router.put("/{income_id}",response_model=IncomeResponse)
def update_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomeUpdate,
    service: IncomeServiceDependency
):
    try:
        return service.update_income(income_id, data)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) from err

    except InvalidIncomeOperationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

@router.patch("/{income_id}",response_model=IncomeResponse)
def patch_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomePatch,
    service: IncomeServiceDependency
):
    try:
        return service.patch_income(income_id, data)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        )

    except InvalidIncomeOperationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )


@router.delete("/{income_id}")
def delete_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return service.delete_income(income_id)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 

@router.get("/reports/inner-join")
def get_income_expenses_inner_join(service: IncomeServiceDependency):
    return service.get_income_expenses_inner_join()