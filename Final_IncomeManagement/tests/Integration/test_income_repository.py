from datetime import date
from decimal import Decimal
import pytest
from app.models.income_expense import Income
from app.repositories.implementations.income_repository import (
    IncomeRepository
)

def make_income():
    return Income(
        income_date=date(2026, 10, 27),
        source="Freelancing",
        income_type="Business",
        amount=Decimal("1000.00"),
        tax_percentage=Decimal("10.00"),
        tax_amount=Decimal("100.00"),
        expense_amount=Decimal("0.00"),
        net_income=Decimal("900.00"),
        cash_in_hand=Decimal("900.00"),
        description="Test income",
    )

@pytest.mark.asyncio
async def test_create_income_in_database(db_session):
    repository = IncomeRepository(db_session)
    income = make_income()
    created = await repository.create(income)
    await db_session.commit()
    assert created.income_id is not None
    assert created.source == "Freelancing"
    assert created.amount == Decimal("1000.00")


@pytest.mark.asyncio
async def test_get_income_by_id(db_session):
    repository = IncomeRepository(db_session)
    income = make_income()
    await repository.create(income)
    await db_session.commit()
    found = await repository.get_by_id(income.income_id)

    assert found is not None
    assert found.income_id == income.income_id
    assert found.source == "Freelancing"


@pytest.mark.asyncio
async def test_get_income_not_found(db_session):
    repository = IncomeRepository(db_session)
    result = await repository.get_by_id(999)
    assert result is None



