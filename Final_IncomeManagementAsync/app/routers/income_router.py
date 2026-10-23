from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status
)
from decimal import Decimal

from app.services.income_service import IncomeService
from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomePaginatedResponse
)

from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch,
    IncomeResponse,
    IncomeByIDResponse,
    IncomePaginatedResponse
)

from app.exceptions.income_exceptions import(
    InvalidIncomeOperationError,
    IncomeNotFoundError
)

from app.dependencies.service_dependecies import get_income_service

router = APIRouter(
    prefix = "/api/income",
    tags = ["Income"]
)


IncomeServiceDependency = Annotated[IncomeService,Depends(get_income_service)]

@router.get("/",response_model=IncomePaginatedResponse)
async def get_all_income(
    service: IncomeServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 5,
    income_name: Annotated[str | None,Query(min_length=1)] = None
):
    return await service.get_incomes(page=page,page_size=page_size,income_name=income_name)


@router.get("/{income_id}",response_model=IncomeByIDResponse)
async def get_one_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return await service.get_income(income_id)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 


@router.post("/",response_model=IncomeResponse,status_code=status.HTTP_201_CREATED)
async def create_income(
    data: IncomeCreate,
    service: IncomeServiceDependency
):
    try:
        return await service.create_income(data)

    except InvalidIncomeOperationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

@router.put("/{income_id}",response_model=IncomeResponse)
async def update_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomeUpdate,
    service: IncomeServiceDependency
):
    try:
        return await service.update_income(income_id, data)
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
async def patch_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomePatch,
    service: IncomeServiceDependency
):
    try:
        return await service.patch_income(income_id, data)
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
async def delete_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return await service.delete_income(income_id)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 

@router.get("/reports/inner-join")
async def get_income_expenses_inner_join(service: IncomeServiceDependency):
    return await service.get_income_expenses_inner_join()


@router.get("/reports/summary")
async def get_income_summary(
    service: IncomeServiceDependency,
    min_expense: Annotated[Decimal | None,Query(ge=0)] = None
):
    return await service.get_income_summary(min_expense)