from datetime import date
from decimal import Decimal
import pytest

from app.services.email_service import EmailSender

# Get all incomes
@pytest.mark.asyncio
async def test_get_all_income(client, admin_headers, income_record):
    response = await client.get("/api/income/",headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()["records"]) == 1
    assert response.json()["records"][0]["source"] == "Freelancing"


# Get income by ID
@pytest.mark.asyncio
async def test_get_income_by_id(client,admin_headers,income_record):
    response = await client.get(
        f"/api/income/{income_record.income_id}",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["income_id"] == income_record.income_id


# Create income
@pytest.mark.asyncio
async def test_create_income_as_admin(client,admin_headers,monkeypatch):
    # prevent sending a real email during testing
    async def skip_email(self, receiver, income):
        return False

    monkeypatch.setattr(
        EmailSender,
        "send_income_confirmation",
        skip_email
    )

    payload = {
        "income_date": date.today().isoformat(),
        "source": "Freelancing",
        "income_type": "Business",
        "amount": "1000.00",
        "tax_percentage": "10.00",
        "expense_amount": "0.00",
        "description": "API test income"
    }

    response = await client.post(
        "/api/income/",
        json=payload,
        headers=admin_headers
    )

    assert response.status_code == 201

    body = response.json()

    assert body["source"] == "Freelancing"
    assert Decimal(body["amount"]) == Decimal("1000.00")
    assert Decimal(body["tax_amount"]) == Decimal("100.00")
    assert Decimal(body["net_income"]) == Decimal("900.00")
    assert Decimal(body["cash_in_hand"]) == Decimal("900.00")


# Update income
@pytest.mark.asyncio
async def test_update_income(client,admin_headers,income_record):

    payload = {
        "income_date": date.today().isoformat(),
        "source": "Salary",
        "income_type": "Job",
        "amount": "2000.00",
        "tax_percentage": "10.00",
        "expense_amount": "100.00",
        "description": "Updated income"
    }

    response = await client.put(
        f"/api/income/{income_record.income_id}",
        json=payload,
        headers=admin_headers
    )

    assert response.status_code == 200
    body = response.json()

    assert body["source"] == "Salary"
    assert Decimal(body["amount"]) == Decimal("2000.00")
    assert Decimal(body["tax_amount"]) == Decimal("200.00")
    assert Decimal(body["net_income"]) == Decimal("1800.00")
    assert Decimal(body["cash_in_hand"]) == Decimal("1700.00")


# Patch income
@pytest.mark.asyncio
async def test_patch_income(client,admin_headers,income_record):
    response = await client.patch(
        f"/api/income/{income_record.income_id}",
        json={"source": "Part-time"},
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["source"] == "Part-time"


# Delete income
@pytest.mark.asyncio
async def test_delete_income(client,admin_headers,income_record):
    response = await client.delete(
        f"/api/income/{income_record.income_id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Income data deleted successfully"


# Income and expense inner join
@pytest.mark.asyncio
async def test_income_expenses_inner_join(client,admin_headers,expense_record):
    response = await client.get(
        "/api/income/reports/inner-join",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["source"] == "Freelancing"


# Income summary
@pytest.mark.asyncio
async def test_income_summary(client,admin_headers, income_record):
    response = await client.get(
        "/api/income/reports/summary",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["income_type"] == "Business"


# Authentication test
@pytest.mark.asyncio
async def test_get_income_without_token_returns_401(client):
    response = await client.get("/api/income/")
    assert response.status_code == 401


# Authorization test
@pytest.mark.asyncio
async def test_create_income_as_regular_user_is_forbidden(client,user_headers):

    payload = {
        "income_date": date.today().isoformat(),
        "source": "Freelancing",
        "income_type": "Business",
        "amount": "1000.00",
        "tax_percentage": "10.00",
        "expense_amount": "0.00"
    }
    response = await client.post(
        "/api/income/",
        json=payload,
        headers=user_headers
    )
    assert response.status_code == 403
