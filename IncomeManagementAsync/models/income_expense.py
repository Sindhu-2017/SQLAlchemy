from datetime import date
from decimal import Decimal
from sqlalchemy import Date,Integer,VARCHAR,Numeric,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database.base import Base


# Income
class Income(Base):
    __tablename__ = "income"

    income_id:Mapped[int] = mapped_column(
        Integer,primary_key = True
    )

    income_date : Mapped[date] = mapped_column(
        Date,nullable = False
    )

    source : Mapped[str] = mapped_column(
        VARCHAR(100),nullable = False
    )

    income_type : Mapped[str] =mapped_column(
        VARCHAR(50),nullable = False
    )

    amount : Mapped[Decimal] = mapped_column(
        Numeric(12,2),nullable = False
    )

    tax_percentage:Mapped[Decimal] = mapped_column(
        Numeric(5,2),nullable=False,default = Decimal(0)
    )

    tax_amount:Mapped[Decimal] = mapped_column(
        Numeric(12,2),nullable=False,default=Decimal(0)
    )

    expense_amount :Mapped[int] =mapped_column(
        Numeric(12,2),nullable=False,default = Decimal(0)
    )

    net_income:Mapped[Decimal] = mapped_column(
        Numeric(12,2),nullable=False,
    )

    cash_in_hand:Mapped[Decimal] = mapped_column(
        Numeric(12,2),nullable=False,
    )

    description:Mapped[str|None] = mapped_column(
        Text,nullable=True
    )

    file_path:Mapped[str|None] = mapped_column(
        Text,nullable=True
    )

    expenses : Mapped[list["Expense"]] = relationship(
        back_populates="income"
    )


# Expense
class Expense(Base):
    __tablename__ = "expense"
    
    expense_id:Mapped[int] = mapped_column(
        Integer,primary_key = True
    )
    income_id: Mapped[int] = mapped_column(
        ForeignKey("income.income_id", ondelete="CASCADE"),
        nullable=False
    )

    expense_name : Mapped[str] = mapped_column(
        VARCHAR(100),nullable = False
    )

    amount : Mapped[Decimal] = mapped_column(
        Numeric(12,2),nullable = False
    )

    description:Mapped[str|None] = mapped_column(
        Text,nullable=True
    )

    income : Mapped["Income"] = relationship(
        back_populates="expenses"
    )
