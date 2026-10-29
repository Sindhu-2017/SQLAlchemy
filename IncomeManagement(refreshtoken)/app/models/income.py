from datetime import date
from decimal import Decimal
from sqlalchemy import (
    Date,
    Integer,
    VARCHAR,
    Numeric,
    Text,
    Index,
    CheckConstraint
)
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base

# Income
class Income(Base):
    __tablename__ = "income"

    __table_args__ = (        
        Index("ix_income_type_date", "income_type", "income_date"),
    )

    income_id:Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    income_date : Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable = False
    )

    source : Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable = False
    )

    income_type : Mapped[str] =mapped_column(
        VARCHAR(50),
        nullable = False
    )

    amount : Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        CheckConstraint("amount > 0"),
        nullable = False
    )

    tax_percentage:Mapped[Decimal] = mapped_column(
        Numeric(5,2),
        CheckConstraint("tax_percentage >= 0 AND tax_percentage <= 100"),
        nullable=False,
        default = Decimal(0),
        server_default="0"
    )

    tax_amount:Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        CheckConstraint("tax_amount >= 0"),
        nullable=False,
        default=Decimal(0),
        server_default="0"
    )

    expense_amount :Mapped[int] =mapped_column(
        Numeric(12,2),
        CheckConstraint("expense_amount >= 0"),
        nullable=False,
        default = Decimal(0),
        server_default="0"
    )

    net_income:Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        CheckConstraint("net_income >= 0"),
        nullable=False,
    )

    cash_in_hand:Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        CheckConstraint("cash_in_hand >= 0"),
        nullable=False,
    )

    description:Mapped[str|None] = mapped_column(
        Text,
        nullable=True
    )

    expenses : Mapped[list["Expense"]] = relationship(
        back_populates="income",
        cascade="all,delete-orphan"
    )

