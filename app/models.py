from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PostIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)
    published: bool = True


class PostOut(PostIn):
    id: int
    created_at: datetime
    user_id: int
    likes: int

    model_config = ConfigDict(from_attributes=True)


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)


class UserOut(UserIn):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
