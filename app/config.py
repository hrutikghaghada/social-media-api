from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_USERNAME: Optional[str] = None
    DATABASE_PASSWORD: Optional[str] = None
    DATABASE_HOSTNAME: Optional[str] = None
    DATABASE_PORT: Optional[str] = None
    DATABASE_NAME: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
