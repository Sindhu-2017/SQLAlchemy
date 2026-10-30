from datetime import date
from decimal import Decimal
import pytest
from app.models.user import User
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_get_income_without_token_returns_401(client):
    response = await client.get("/api/income/")
    assert response.status_code == 401
    assert response.json()["detail"] == ("Not authenticated")


@pytest.mark.asyncio
async def test_create_income_as_admin(client, db_session):
    admin = User(
        username="testadmin",
        email="admin@example.com",
        hashed_password="not-used-in-this-test",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    token = create_access_token(
        user_id=admin.user_id,
        role=admin.role
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "income_date": date.today().isoformat(),
        "source": "Freelancing",
        "income_type": "Business",
        "amount": "1000.00",
        "tax_percentage": "10.00",
        "expense_amount": "100.00",
        "description": "API test income"
    }

    response = await client.post(
        "/api/income/",
        json=payload,
        headers=headers
    )
    assert response.status_code == 201
    body = response.json()

    assert body["source"] == "Freelancing"
    assert body["income_type"] == "Business"
    assert Decimal(body["amount"]) == Decimal("1000.00")
    assert Decimal(body["tax_amount"]) == Decimal("100.00")
    assert Decimal(body["net_income"]) == Decimal("900.00")
    assert Decimal(body["cash_in_hand"]) == Decimal("800.00")


@pytest.mark.asyncio
async def test_create_income_as_regular_user_is_forbidden(
    client,
    db_session,
):
    user = User(
        username="testuser",
        email="user@example.com",
        hashed_password="not-used-in-this-test",
        role="user",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token(
        user_id=user.user_id,
        role=user.role
    )

    response = await client.post(
        "/api/income/",
        json={
            "income_date": date.today().isoformat(),
            "source": "Freelancing",
            "income_type": "Business",
            "amount": "1000.00",
            "tax_percentage": "10.00",
            "expense_amount": "100.00"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 403
