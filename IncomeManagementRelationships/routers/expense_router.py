from typing import Annotated
from fastapi import (
    APIRouter, Depends, HTTPException, Path, status
)
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.expense_service import ExpenseService
from schemas.expense import ExpenseCreate, ExpensePatch
from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError,
)

router = APIRouter(prefix="/api/expenses",tags=["Expenses"])


def get_expense_service(db: Session = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)

ExpenseServiceDependency = Annotated[ExpenseService,Depends(get_expense_service)]

@router.post("/income/{income_id}",status_code=status.HTTP_201_CREATED)
def add_expense(
    income_id: Annotated[int, Path(gt=0)],
    data: ExpenseCreate,
    service: ExpenseServiceDependency
):
    try:
        return service.add_expense(income_id, data)
    except IncomeNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except InvalidIncomeOperationError as err:
        raise HTTPException(status_code=422, detail=str(err))


@router.get("/income/{income_id}")
def get_expenses(
    income_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        return service.get_expenses(income_id)
    except IncomeNotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.patch("/{expense_id}")
def patch_expense(
    expense_id: Annotated[int, Path(gt=0)],
    data: ExpensePatch,
    service: ExpenseServiceDependency
):
    try:
        return service.patch_expense(expense_id, data)
    except InvalidIncomeOperationError as err:
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(status_code=status_code, detail=str(err))


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: Annotated[int, Path(gt=0)],
    service: ExpenseServiceDependency
):
    try:
        return service.delete_expense(expense_id)
    except InvalidIncomeOperationError as err:
        status_code = 404 if "not found" in str(err).lower() else 422
        raise HTTPException(status_code=status_code, detail=str(err))


@router.get("/reports/left-outer-join")
def get_income_expenses_outer_join(service: ExpenseServiceDependency):
    return service.get_income_expenses_outer_join()

