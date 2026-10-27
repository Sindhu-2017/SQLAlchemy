
import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "pytest_user",
            "email": "pytest@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["username"] == "pytest_user"
    assert body["email"] == "pytest@example.com"
    assert body["role"] == "user"
    assert body["is_active"] is True

    # The API must never return the password hash.
    assert "hashed_password" not in body
    assert "password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_user_returns_409(client):
    payload = {
        "username": "duplicate_user",
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
    }

    first_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/api/auth/register",
        json=payload,
    )

    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_register_with_short_password_returns_422(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "shortpass",
            "email": "shortpass@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422
