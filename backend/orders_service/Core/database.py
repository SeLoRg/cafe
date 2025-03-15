from common.Database import DataBase
from .config import settings

database = DataBase(
    settings.async_postgres_url, echo=False, autoflush=False, autocommit=False
)
