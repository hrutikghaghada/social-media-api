import logging
from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.database import database, user_table
from app.models import Token, UserIn
from app.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
)

router = APIRouter(tags=["Users"])

logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserIn):
    logger.info("Registering a user", extra={"email": user.email})

    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    query = user_table.insert().values(
        email=user.email, password=get_password_hash(user.password)
    )
    await database.execute(query)
    return {"detail": "User created"}


@router.post("/token", response_model=Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = user_credentials.username
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format",
        )

    logger.info("Logging in a user", extra={"email": email})

    user = await authenticate_user(email, user_credentials.password)
    access_token = create_access_token(user.email)

    return {"access_token": access_token, "token_type": "bearer"}
