import pytest
from httpx import AsyncClient

from app import security
from app.models import PostOut


async def create_post(
    async_client: AsyncClient,
    logged_in_token: str,
    title: str,
    content: str,
    published: bool,
) -> dict:
    response = await async_client.post(
        "/posts/",
        json={"title": title, "content": content, "published": published},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def like_post(
    async_client: AsyncClient, logged_in_token: str, post_id: int
) -> dict:
    response = await async_client.post(
        f"/like/{post_id}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_user(async_client: AsyncClient, email: str, password: str) -> dict:
    response = await async_client.post(
        "/register", json={"email": email, "password": password}
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str) -> dict:
    return await create_post(
        async_client,
        logged_in_token,
        title="Test title",
        content="Test content",
        published=True,
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "awesome new content", True),
        ("favorite pizza", "i love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
    ],
)
async def test_create_post(
    async_client: AsyncClient,
    registered_user: dict,
    logged_in_token: str,
    title: str,
    content: str,
    published: bool,
):
    response = await async_client.post(
        "/posts/",
        json={
            "title": title,
            "content": content,
            "published": published,
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    post_created = PostOut(**response.json())
    assert response.status_code == 201
    assert post_created.title == title
    assert post_created.content == content
    assert post_created.published == published
    assert post_created.user_id == registered_user["id"]


@pytest.mark.anyio
async def test_create_post_expired_token(
    async_client: AsyncClient,
    registered_user: dict,
    mocker,
):
    mocker.patch("app.security.access_token_require_minutes", return_value=-1)
    token = security.create_access_token(registered_user["email"])

    response = await async_client.post(
        "/posts/",
        json={
            "title": "Test title",
            "content": "Test content",
            "published": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "title, content",
    [
        ("", "Test content"),
        ("Test title", ""),
        (None, "Test content"),
        ("Test title", None),
        ("", ""),
    ],
)
async def test_create_post_invalid_data(
    async_client: AsyncClient, logged_in_token: str, title: str, content: str
):
    response = await async_client.post(
        "/posts/",
        json={
            "title": title,
            "content": content,
            "published": True,
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(
    async_client: AsyncClient, logged_in_token: str, created_post: dict
):
    response = await async_client.get(
        "/posts/", headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 200
    assert created_post.items() <= response.json()[0].items()


@pytest.mark.anyio
async def test_get_all_posts_sort_likes(
    async_client: AsyncClient, logged_in_token: str
):
    post_1 = await create_post(
        async_client, logged_in_token, "Test Post 1", "Content", True
    )
    post_2 = await create_post(
        async_client, logged_in_token, "Test Post 2", "Content", True
    )

    await like_post(async_client, logged_in_token, post_2["id"])

    response = await async_client.get(
        "/posts/",
        params={"sorting": "most_likes"},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert [post["id"] for post in data] == [post_2["id"], post_1["id"]]


@pytest.mark.anyio
async def test_get_all_post_wrong_sorting(
    async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.get(
        "/posts/",
        params={"sorting": "wrong"},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/posts/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_one_post(
    async_client: AsyncClient, logged_in_token: str, created_post: dict
):
    response = await async_client.get(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 200
    assert created_post.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_one_post_not_found(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.get(
        "/posts/99999",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404
    assert "Post not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_one_post_unauthorized(async_client: AsyncClient, created_post: dict):
    response = await async_client.get(f"/posts/{created_post['id']}")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.anyio
async def test_delete_post(
    async_client: AsyncClient, logged_in_token: str, created_post: dict
):
    response = await async_client.delete(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 204

    response = await async_client.get(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404
    assert "Post not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_delete_post_not_found(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.delete(
        "/posts/99999",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404
    assert "Post not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_delete_post_unauthorized(async_client: AsyncClient, created_post: dict):
    response = await async_client.delete(f"/posts/{created_post['id']}")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.anyio
async def test_delete_other_user_post(
    async_client: AsyncClient, logged_in_token: str, created_post: dict
):
    await create_post(
        async_client,
        logged_in_token,
        title="Test title",
        content="Test content",
        published=True,
    )

    await create_user(async_client, email="user2@gmail.com", password="test_password")
    token = security.create_access_token(email="user2@gmail.com")

    response = await async_client.delete(
        f"/posts/{created_post['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "Not authorized to perform requested action" in response.json()["detail"]


@pytest.mark.anyio
async def test_update_post(
    async_client: AsyncClient, logged_in_token: str, created_post: dict
):
    response = await async_client.put(
        f"/posts/{created_post['id']}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": False,
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Updated content"
    assert response.json()["published"] is False


@pytest.mark.anyio
async def test_update_post_not_found(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.put(
        "/posts/99999",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": False,
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404
    assert "Post not found" in response.json()["detail"]


@pytest.mark.anyio
async def test_update_post_unauthorized(async_client: AsyncClient, created_post: dict):
    response = await async_client.put(
        f"/posts/{created_post['id']}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": False,
        },
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.anyio
async def test_update_other_user_post(async_client: AsyncClient, created_post: dict):
    await create_user(async_client, email="user2@gmail.com", password="test_password")
    token = security.create_access_token(email="user2@gmail.com")

    response = await async_client.put(
        f"/posts/{created_post['id']}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "Not authorized to perform requested action" in response.json()["detail"]
