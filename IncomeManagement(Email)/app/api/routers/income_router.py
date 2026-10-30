import logging
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

from app.api.dependencies.service_dependecies import get_income_service
from app.api.dependencies.auth import (
    get_current_user,
    require_roles
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/api/income",
    tags = ["Income"]
)

IncomeServiceDependency = Annotated[IncomeService,Depends(get_income_service)]


# get all incomes
@router.get(
    "/",
    response_model=IncomePaginatedResponse,
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_all_income(
    service: IncomeServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 5,
    income_name: Annotated[str | None,Query(min_length=1)] = None
):
    return await service.get_incomes(page=page,page_size=page_size,income_name=income_name)


# get by income id
@router.get(
    "/{income_id}",
    response_model=IncomeByIDResponse,
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_one_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return await service.get_income(income_id)
    except IncomeNotFoundError as err:
        logger.warning("Income lookup rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 


# create income
@router.post(
    "/",
    response_model=IncomeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))]
)
async def create_income(
    data: IncomeCreate,
    service: IncomeServiceDependency,
    current_user : Annotated[User,Depends(get_current_user)]
):
    try:
        return await service.create_income(data,current_user.email)

    except InvalidIncomeOperationError as err:
        logger.warning("Income creation rejected: %s", str(err))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

# update income
@router.put(
    "/{income_id}",
    response_model=IncomeResponse,
    dependencies=[Depends(require_roles("admin"))]
)
async def update_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomeUpdate,
    service: IncomeServiceDependency
):
    try:
        return await service.update_income(income_id, data)
    except IncomeNotFoundError as err:
        logger.warning("Income update rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) from err

    except InvalidIncomeOperationError as err:
        logger.warning("Income update rejected: %s", str(err))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )


# patch income
@router.patch(
    "/{income_id}",
    response_model=IncomeResponse,
    dependencies=[Depends(require_roles("admin"))]
)
async def patch_income(
    income_id: Annotated[int, Path(gt=0)],
    data: IncomePatch,
    service: IncomeServiceDependency
):
    try:
        return await service.patch_income(income_id, data)
    except IncomeNotFoundError as err:
        logger.warning("Income patch rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        )

    except InvalidIncomeOperationError as err:
        logger.warning("Income patch rejected: %s", str(err))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )


# delete income
@router.delete(
    "/{income_id}",
    dependencies=[Depends(require_roles("admin"))]
)
async def delete_income(
    income_id: Annotated[int, Path(gt=0)],
    service: IncomeServiceDependency
):
    try:
        return await service.delete_income(income_id)
    except IncomeNotFoundError as err:
        logger.warning("Income deletion rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err)
        ) 

# inner join
@router.get(
    "/reports/inner-join",
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_income_expenses_inner_join(service: IncomeServiceDependency):
    return await service.get_income_expenses_inner_join()


# summary
@router.get(
    "/reports/summary",
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_income_summary(
    service: IncomeServiceDependency,
    min_expense: Annotated[Decimal | None,Query(ge=0)] = None
):
    return await service.get_income_summary(min_expense)