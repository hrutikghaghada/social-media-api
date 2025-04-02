import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.database import database, like_table
from app.models import UserOut
from app.routes.post import find_post
from app.security import get_current_user

router = APIRouter(prefix="/like", tags=["Likes"])

logger = logging.getLogger(__name__)


@router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int,
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    logger.info(f"Liking a post with id {post_id}")

    await find_post(post_id)

    select_query = like_table.select().where(
        like_table.c.user_id == current_user.id,
        like_table.c.post_id == post_id,
    )
    existing_like = await database.fetch_one(select_query)

    if existing_like:
        delete_query = like_table.delete().where(
            like_table.c.user_id == current_user.id,
            like_table.c.post_id == post_id,
        )
        await database.execute(delete_query)
        return {"detail": "Like removed successfully"}

    insert_query = like_table.insert().values(
        user_id=current_user.id,
        post_id=post_id,
    )
    await database.execute(insert_query)
    return {"detail": "Like added successfully"}
