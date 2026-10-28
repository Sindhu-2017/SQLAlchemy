from decimal import Decimal
from unittest.mock import AsyncMock, Mock
import pytest

from app.services.income_service import IncomeService
from app.exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError
)


@pytest.fixture
def service():
    # mock all external dependencies
    db = Mock()
    income_repository = Mock()
    expense_repository = Mock()

    return IncomeService(
        db=db,
        repository=income_repository,
        expense_repository=expense_repository,
    )

@pytest.mark.asyncio
async def test_calculate_income_success(service):
    tax, net_income, cash_in_hand = (
        await service.calculate_income(
            amount=Decimal("1000"),
            tax_percentage=Decimal("10"),
            expense_amount=Decimal("100"),
        )
    )

    assert tax == Decimal("100")
    assert net_income == Decimal("900")
    assert cash_in_hand == Decimal("800")


@pytest.mark.asyncio
async def test_calculate_income_zero_tax(service):
    tax, net_income, cash_in_hand = (
        await service.calculate_income(
            amount=Decimal("1000"),
            tax_percentage=Decimal("0"),
            expense_amount=Decimal("200"),
        )
    )

    assert tax == Decimal("0")
    assert net_income == Decimal("1000")
    assert cash_in_hand == Decimal("800")


@pytest.mark.asyncio
async def test_expenses_cannot_exceed_net_income(service):
    with pytest.raises(InvalidIncomeOperationError):
        await service.calculate_income(
            amount=Decimal("1000"),
            tax_percentage=Decimal("10"),
            expense_amount=Decimal("901"),
        )


@pytest.mark.asyncio
async def test_negative_expense_is_rejected(service):
    with pytest.raises(InvalidIncomeOperationError):
        await service.calculate_income(
            amount=Decimal("1000"),
            tax_percentage=Decimal("10"),
            expense_amount=Decimal("-1"),
        )


@pytest.mark.asyncio
async def test_get_income_success(service):
    expected_income = Mock()
    expected_income.income_id = 1

    service.repository.get_by_id = AsyncMock(
        return_value=expected_income
    )
    result = await service.get_income(1)
    assert result.income_id == 1
    service.repository.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_income_not_found(service):
    service.repository.get_by_id = AsyncMock(
        return_value=None
    )
    with pytest.raises(IncomeNotFoundError):
        await service.get_income(999)
    service.repository.get_by_id.assert_awaited_once_with(999)
