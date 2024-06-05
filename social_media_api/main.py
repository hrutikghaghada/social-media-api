from contextlib import asynccontextmanager

from fastapi import FastAPI

from social_media_api.database import database
from social_media_api.routers.posts import router as post_router
from social_media_api.routers.users import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router)
app.include_router(user_router)
