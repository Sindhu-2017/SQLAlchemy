from sqlalchemy import (
    Integer,
    String,
    Numeric,
    Text,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from database.base import Base


class Expense(Base):
    __tablename__ = "expense"

    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="check_expense_amount_non_negative"
        ),
    )

    expense_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    income_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("income.income_id", ondelete="CASCADE"),
        nullable=False
    )

    expense_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Many expenses belong to one income
    income: Mapped["Income"] = relationship(
        back_populates="expenses"
    )
