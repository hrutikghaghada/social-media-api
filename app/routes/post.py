import logging
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.database import database, like_table, post_table
from app.models import PostIn, PostOut, UserOut
from app.security import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(
        post_table, sqlalchemy.func.count(like_table.c.post_id).label("likes")
    )
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")

    query = post_table.select().where(post_table.c.id == post_id)
    post = await database.fetch_one(query)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get("/", response_model=list[PostOut])
async def get_posts(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    limit: Annotated[int, Query(gt=0)] = 10,
    skip: Annotated[int, Query(ge=0)] = 0,
    search: str = "",
):
    logger.info("Getting all posts")

    query = (
        select_post_and_likes.filter(post_table.c.title.contains(search))
        .offset(skip)
        .limit(limit)
    )
    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    await find_post(post_id)
    query = select_post_and_likes.filter(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostIn,
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    logger.info("Creating a post")

    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(**data)
    last_record_id = await database.execute(query)
    return await find_post(last_record_id)


@router.put("/{post_id}", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def update_post(
    post_id: int,
    updated_post: PostIn,
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    logger.info(f"Updating post with id {post_id}")

    post = await find_post(post_id)

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    data = updated_post.model_dump()
    query = post_table.update().where(post_table.c.id == post_id).values(**data)

    await database.execute(query)
    return await find_post(post_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    logger.info(f"Deleting post with id {post_id}")

    post = await find_post(post_id)

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    query = post_table.delete().where(post_table.c.id == post_id)
    await database.execute(query)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
