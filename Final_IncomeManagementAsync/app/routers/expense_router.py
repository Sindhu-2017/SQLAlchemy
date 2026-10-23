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

router = APIRouter(
    prefix="/api/expenses",
    tags=["Expenses"]
)


ExpenseServiceDependency = Annotated[ExpenseService,Depends(get_expense_service)]

@router.post("/income/{income_id}",status_code=status.HTTP_201_CREATED)
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


@router.get("/income/{income_id}",response_model=list[ExpenseResponse])
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


@router.patch("/{expense_id}")
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


@router.delete("/{expense_id}")
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


@router.get("/reports/left-outer-join")
async def get_income_expenses_outer_join(service: ExpenseServiceDependency):
    
    return await service.get_income_expenses_outer_join()

