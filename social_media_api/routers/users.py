from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from social_media_api import tasks
from social_media_api.database import database, user_table
from social_media_api.models.user import UserIn
from social_media_api.security import (
    authenticate_user,
    create_access_token,
    create_confirmation_token,
    get_password_hash,
    get_subject_for_token_type,
    get_user,
)

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn, request: Request, background_tasks: BackgroundTasks):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)

    await database.execute(query)

    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    )

    return {"detail": "User created. Please confirm your email."}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )

    await database.execute(query)
    return {"detail": "User confirmed"}
