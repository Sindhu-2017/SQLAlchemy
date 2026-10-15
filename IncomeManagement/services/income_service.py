
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from models.income import Income
from repositories.income_repository import IncomeRepository
from schemas.income import IncomeCreate, IncomeUpdate, IncomePatch

from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError
)

class IncomeService:

    BASE_UPLOAD_DIR = (Path(__file__).resolve().parent.parent/ "uploads"/ "income")
    ALLOWED_FILE_TYPES = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }
    MAX_FILE_SIZE = 5 * 1024 * 1024
    CHUNK_SIZE = 1024 * 1024  

    def __init__(self, db: Session):
        self.db = db
        self.repository = IncomeRepository(db)

    @staticmethod
    def calculate_income(amount: Decimal,tax_percentage: Decimal,expense_amount: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        tax_amount = amount * tax_percentage / 100
        net_income = amount - tax_amount
        cash_in_hand = net_income - expense_amount

        if expense_amount < 0 or cash_in_hand < 0:
            raise InvalidIncomeOperationError("Expenses cannot exceed net income." )
        return tax_amount, net_income, cash_in_hand

    def create_income(self, data: IncomeCreate) -> Income:
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(data.amount,data.tax_percentage,data.expense_amount)
        )

        income = Income(
            income_date=data.income_date,
            source=data.source,
            income_type=data.income_type,
            amount=data.amount,
            tax_percentage=data.tax_percentage,
            tax_amount=tax_amount,
            expense_amount=Decimal("0"),
            net_income=net_income,
            cash_in_hand=cash_in_hand,
            description=data.description,
        )

        try:
            self.repository.create(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception:
            self.db.rollback()
            raise

    def get_income(self, income_id: int) -> Income:
        income = self.repository.get_by_id(income_id)
        if income is None:
            raise IncomeNotFoundError(income_id)
        return income

    def get_incomes(self,page: int,page_size: int,income_name: str | None = None) -> dict:
        records, total = self.repository.get_all(
            page=page,
            page_size=page_size,
            income_name=income_name
        )
        offset = (page - 1) * page_size
        total_pages = ((total + page_size - 1) // page_size if total else 0)

        return {
            "records": records,
            "pagination": {
                "total_records": total,
                "page_size": page_size,
                "offset": offset,
                "total_pages": total_pages,
                "page_number": page,
                "has_previous": page > 1 and total > 0,
                "has_next": page < total_pages,
            }
        }

    def update_income(self,income_id: int,data: IncomeUpdate) -> Income:
        income = self.get_income(income_id)
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(data.amount,data.tax_percentage,data.expense_amount)
        )
        changes = data.model_dump()
        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)

            self.repository.update(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception:
            self.db.rollback()
            raise

    def patch_income(self,income_id: int, data: IncomePatch) -> Income:
        income = self.get_income(income_id)
        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise InvalidIncomeOperationError("Provide at least one field to update.")
        
        for field, value in changes.items():
            if value is None and field != "description":
                raise InvalidIncomeOperationError(f"{field} cannot be null.")

        amount = changes.get("amount", income.amount)
        tax_percentage = changes.get("tax_percentage",income.tax_percentage)
        expense_amount = changes.get("expense_amount",income.expense_amount)
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(amount,tax_percentage,expense_amount)
        )
        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)

            self.repository.update(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception:
            self.db.rollback()
            raise

    
    def update_expense_using_procedure(self,income_id: int,expense_amount: Decimal) -> Income:
        if expense_amount < 0:
            raise InvalidIncomeOperationError("Expense amount cannot be negative.")
        income = self.get_income(income_id)

        try:
            self.repository.update_expense_using_procedure(income_id=income_id,expense_amount=expense_amount)
            self.db.commit()
            self.db.refresh(income)
            return income

        except Exception:
            self.db.rollback()
            raise


    def delete_income(self, income_id: int) -> None:
        income = self.get_income(income_id)
        try:
            self.repository.delete(income)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    async def upload_income_file(self,income_id: int,file: UploadFile) -> dict:
        income = self.get_income(income_id)
        if file.content_type not in self.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, JPG and PNG files are allowed"
            )
        income_directory = self.BASE_UPLOAD_DIR / str(income_id)
        income_directory.mkdir(parents=True,exist_ok=True)

        extension = self.ALLOWED_FILE_TYPES[file.content_type]
        unique_filename = f"{uuid4().hex}{extension}"
        destination = income_directory / unique_filename

        total_size = 0

        try:
            async with aiofiles.open(destination, "wb") as output:
                while True:
                    chunk = await file.read(self.CHUNK_SIZE)
                    if not chunk:
                        break

                    total_size += len(chunk)
                    if total_size > self.MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="File size cannot exceed 5 MB"
                        )
                    await output.write(chunk)

            relative_path = destination.relative_to(self.BASE_UPLOAD_DIR.parent.parent).as_posix()

            try:
                self.repository.update_file_path(income=income,file_path=relative_path)
                self.db.commit()
                self.db.refresh(income)
            except Exception:
                self.db.rollback()
                raise

            return {
                "message": "Income file uploaded successfully",
                "income_id": income_id,
                "file_path": relative_path
            }

        except Exception:
            destination.unlink(missing_ok=True)
            raise

        finally:
            await file.close()
