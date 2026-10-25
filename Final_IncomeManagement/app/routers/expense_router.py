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
from app.dependencies.service_dependecies import get_expense_service
from app.dependencies.auth import require_permissions

router = APIRouter(
    prefix="/api/expenses",
    tags=["Expenses"]
)


ExpenseServiceDependency = Annotated[ExpenseService,Depends(get_expense_service)]

# create expense based on income id
@router.post(
    "/income/{income_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("expense:create"))]
)
async def add_expense(
    income_id: Annotated[int, Path(gt=0)],
    data: ExpenseCreate,
    service: ExpenseServiceDependency
):
    try:
        return await service.add_expense(income_id, data)
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=404, 
            detail=str(err)
        )
    except InvalidIncomeOperationError as err:
        raise HTTPException(
            status_code=422, 
            detail=str(err)
        )


# get by income id
@router.get(
    "/income/{income_id}",
    response_model=list[ExpenseResponse],
    dependencies=[Depends(require_permissions("expense:read"))]
)
async def get_expenses(
    income_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        return await service.get_expenses(income_id)
    
    except IncomeNotFoundError as err:
        raise HTTPException(
            status_code=404, 
            detail=str(err)
        )


# patch income
@router.patch(
    "/{expense_id}",
    dependencies=[Depends(require_permissions("expense:update"))]
)
async def patch_expense(
    expense_id: Annotated[int, Path(gt=0)],
    data: ExpensePatch,
    service: ExpenseServiceDependency
):
    try:
        return await service.patch_expense(expense_id, data)
    
    except InvalidIncomeOperationError as err:
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(
            status_code=status_code, 
            detail=str(err)
        )


# delete expense
@router.delete(
    "/{expense_id}",
    dependencies=[Depends(require_permissions("expense:delete"))]
)
async def delete_expense(
    expense_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        return await service.delete_expense(expense_id)
    
    except InvalidIncomeOperationError as err:
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(
            status_code=status_code, 
            detail=str(err)
        )


# left outer join
@router.get(
    "/reports/left-outer-join",
    dependencies=[Depends(require_permissions("expense:read"))]
)
async def get_income_expenses_outer_join(service: ExpenseServiceDependency):
    
    return await service.get_income_expenses_outer_join()

