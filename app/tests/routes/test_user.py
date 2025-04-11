import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@email.com", "test_password")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await register_user(
        async_client, registered_user["email"], "test_password"
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("test@.com", "test_password", 422),
        ("test@com", "test_password", 422),
        ("test@com.", "test_password", 422),
        ("test@.com.", "test_password", 422),
        ("test@com..com", "test_password", 422),
        ("test@example.com", "test_password", 422),
        ("test@email.com", "abc", 422),
        (None, "test_password", 422),
        ("test@email.com", None, 422),
    ],
)
async def test_register_user_invalid_inputs(
    async_client: AsyncClient,
    email: str,
    password: str,
    status_code: int,
):
    response = await register_user(async_client, email, password)
    assert response.status_code == status_code


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/token",
        data={
            "username": "user@email.com",
            "password": "test_password",
        },
    )
    assert response.status_code == 401


@pytest.mark.anyio
@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "test_password", 401),
        ("test@email.com", "wrong_password", 401),
        ("wrongemail@gmail.com", "wrong_password", 401),
        ("test@email.com", None, 401),
        (None, "test_password", 422),
    ],
)
async def test_login_user_invalid_credentials(
    async_client: AsyncClient,
    registered_user: dict,
    email: str,
    password: str,
    status_code: int,
):
    response = await async_client.post(
        "/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == status_code
