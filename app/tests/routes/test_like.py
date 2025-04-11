import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient,
    logged_in_token: str,
    created_post: dict,
):
    response = await async_client.post(
        f"/like/{created_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 201
    assert response.json() == {"detail": "Like added successfully"}


@pytest.mark.anyio
async def test_unlike_post(
    async_client: AsyncClient,
    logged_in_token: str,
    liked_post: dict,
):
    response = await async_client.post(
        f"/like/{liked_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 201
    assert response.json() == {"detail": "Like removed successfully"}


@pytest.mark.anyio
async def test_like_post_not_found(
    async_client: AsyncClient,
    logged_in_token: str,
):
    response = await async_client.post(
        "/like/99999",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


@pytest.mark.anyio
async def test_like_post_unauthorized(
    async_client: AsyncClient,
    created_post: dict,
):
    response = await async_client.post(
        f"/like/{created_post['id']}",
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
