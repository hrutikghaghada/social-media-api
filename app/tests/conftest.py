import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

os.environ["ENV_STATE"] = "test"

from app.database import database, user_table
from app.main import app
from app.tests.routes.test_post import create_post


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@email.com", "password": "test_password"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    if user is not None:
        user_details["id"] = user["id"]
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    response = await async_client.post(
        "/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    return response.json()["access_token"]


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str) -> dict:
    return await create_post(
        async_client,
        logged_in_token,
        title="Test title",
        content="Test content",
        published=True,
    )


@pytest.fixture()
async def liked_post(
    async_client: AsyncClient,
    logged_in_token: str,
    created_post: dict,
) -> dict:
    await async_client.post(
        f"/like/{created_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    return created_post
