from datetime import date
from decimal import Decimal

import pytest


# Get expenses by income ID
@pytest.mark.asyncio
async def test_get_expenses(
    client,
    admin_headers,
    expense_record
):

    response = await client.get(
        f"/api/expenses/income/{expense_record.income_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["expense_name"] == "Electricity Bill"



# Delete expense
@pytest.mark.asyncio
async def test_delete_expense(
    client,
    admin_headers,
    expense_record
):

    response = await client.delete(
        f"/api/expenses/{expense_record.expense_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "Expense deleted successfully"
    assert Decimal(str(body["expense_amount"])) == Decimal("0.00")
    assert Decimal(str(body["cash_in_hand"])) == Decimal("900.00")


# Left outer join
@pytest.mark.asyncio
async def test_income_expenses_outer_join(
    client,
    admin_headers,
    expense_record
):

    response = await client.get(
        "/api/expenses/reports/left-outer-join",
        headers=admin_headers
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["source"] == "Freelancing"
    assert len(body[0]["expenses"]) == 1
    assert body[0]["expenses"][0]["expense_name"] == "Electricity Bill"


# Authentication test
@pytest.mark.asyncio
async def test_get_expenses_without_token_returns_401(
    client,
    income_record
):

    response = await client.get(
        f"/api/expenses/income/{income_record.income_id}"
    )

    assert response.status_code == 401


# Authorization test
@pytest.mark.asyncio
async def test_add_expense_as_regular_user_is_forbidden(
    client,
    user_headers,
    income_record
):

    response = await client.post(
        f"/api/expenses/income/{income_record.income_id}",
        json={
            "expense_name": "Electricity Bill",
            "amount": "100.00",
            "payment_method": "UPI",
            "expense_date": date.today().isoformat()
        },
        headers=user_headers
    )

    assert response.status_code == 403
