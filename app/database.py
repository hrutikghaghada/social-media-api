import databases
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql.expression import text

from app.config import config

metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("content", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "published", sqlalchemy.Boolean, server_default="TRUE", nullable=False
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
)

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    ),
)

like_table = sqlalchemy.Table(
    "likes",
    metadata,
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "post_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

DATABASE_URL = f"postgresql+asyncpg://{config.DATABASE_USERNAME}:{config.DATABASE_PASSWORD}@{config.DATABASE_HOSTNAME}:{config.DATABASE_PORT}/{config.DATABASE_NAME}"

engine = create_async_engine(DATABASE_URL)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


database = databases.Database(DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK)
