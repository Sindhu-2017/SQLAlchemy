import pytest_asyncio

from datetime import date
from decimal import Decimal

from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense

from app.core.security import create_access_token


@pytest_asyncio.fixture
async def admin_headers(db_session):

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

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest_asyncio.fixture
async def user_headers(db_session):

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

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest_asyncio.fixture
async def income_record(db_session):

    income = Income(
        income_date=date.today(),
        source="Freelancing",
        income_type="Business",
        amount=Decimal("1000.00"),
        tax_percentage=Decimal("10.00"),
        tax_amount=Decimal("100.00"),
        expense_amount=Decimal("0.00"),
        net_income=Decimal("900.00"),
        cash_in_hand=Decimal("900.00"),
        description="Test income"
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

    return income


@pytest_asyncio.fixture
async def expense_record(db_session, income_record):

    expense = Expense(
        income_id=income_record.income_id,
        expense_name="Electricity Bill",
        amount=Decimal("100.00"),
        payment_method="UPI",
        expense_date=date.today(),
        description="Test expense"
    )

    db_session.add(expense)
    await db_session.commit()
    await db_session.refresh(expense)

    return expense
