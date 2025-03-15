from common.config import Postgres
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(Postgres):
    model_config = SettingsConfigDict()


settings = Settings()
