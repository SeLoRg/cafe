from common.config import Postgres, Elastic, Redis
from pydantic_settings import SettingsConfigDict


class Settings(Postgres, Elastic, Redis):
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
