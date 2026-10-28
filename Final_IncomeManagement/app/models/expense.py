from datetime import date
from decimal import Decimal
from sqlalchemy import Date,Integer,VARCHAR,Numeric,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base
# Expense
class Expense(Base):
    __tablename__ = "expense"
    
    expense_id:Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )
    income_id: Mapped[int] = mapped_column(
        ForeignKey("income.income_id", ondelete="CASCADE"),
        nullable=False
    )

    expense_name : Mapped[str] = mapped_column(
        VARCHAR(100),
        nullable = False
    )

    payment_method: Mapped[str] = mapped_column(
        VARCHAR(30),
        nullable=False
    )

    amount : Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        nullable = False
    )

    description:Mapped[str|None] = mapped_column(
        Text,
        nullable=True
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    income : Mapped["Income"] = relationship(
        back_populates="expenses"
    )
