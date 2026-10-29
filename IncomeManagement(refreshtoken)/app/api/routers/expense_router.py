import logging
from typing import Annotated
from fastapi import (
    APIRouter, Depends, HTTPException, Path, status
)

from app.services.expense_service import ExpenseService
from app.schemas.expense import ExpenseCreate, ExpensePatch,ExpenseResponse
from app.exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError,
)
from app.api.dependencies.service_dependecies import get_expense_service
from app.api.dependencies.auth import require_roles

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/expenses",
    tags=["Expenses"]
)

ExpenseServiceDependency = Annotated[ExpenseService,Depends(get_expense_service)]

# create expense based on income id
@router.post(
    "/income/{income_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))]
)
async def add_expense(
    income_id: Annotated[int, Path(gt=0)],
    data: ExpenseCreate,
    service: ExpenseServiceDependency
):
    try:
        result = await service.add_expense(income_id, data)
        logger.info("Expense created for income_id=%s", income_id)
        return result
    except IncomeNotFoundError as err:
        logger.warning("Expense creation rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=404, 
            detail=str(err)
        )
    except InvalidIncomeOperationError as err:
        logger.warning("Expense creation rejected: %s", str(err))
        raise HTTPException(
            status_code=422, 
            detail=str(err)
        )


# get by income id
@router.get(
    "/income/{income_id}",
    response_model=list[ExpenseResponse],
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_expenses(
    income_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        return await service.get_expenses(income_id)
    
    except IncomeNotFoundError as err:
        logger.warning("Expense lookup rejected: income_id=%s not found", income_id)
        raise HTTPException(
            status_code=404, 
            detail=str(err)
        )


# patch income
@router.patch(
    "/{expense_id}",
    dependencies=[Depends(require_roles("admin"))]
)
async def patch_expense(
    expense_id: Annotated[int, Path(gt=0)],
    data: ExpensePatch,
    service: ExpenseServiceDependency
):
    try:
        result = await service.patch_expense(expense_id, data)
        logger.info("Expense updated: expense_id=%s", expense_id)
        return result
    
    except InvalidIncomeOperationError as err:
        logger.warning("Expense update rejected: expense_id=%s | %s", expense_id, str(err))
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(
            status_code=status_code, 
            detail=str(err)
        )


# delete expense
@router.delete(
    "/{expense_id}",
    dependencies=[Depends(require_roles("admin"))]
)
async def delete_expense(
    expense_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        result = await service.delete_expense(expense_id)
        logger.info("Expense deleted: expense_id=%s", expense_id)
        return result
    
    except InvalidIncomeOperationError as err:
        logger.warning("Expense deletion rejected: expense_id=%s | %s", expense_id, str(err))
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(
            status_code=status_code, 
            detail=str(err)
        )


# left outer join
@router.get(
    "/reports/left-outer-join",
    dependencies=[Depends(require_roles("admin","user"))]
)
async def get_income_expenses_outer_join(service: ExpenseServiceDependency):
    
    return await service.get_income_expenses_outer_join()

