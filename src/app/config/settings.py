from functools import lru_cache

from pydantic_settings import BaseSettings

from app.config.database import DatabaseConfig
from app.config.engine import EngineConfig


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        database: Configuration for the database.
        engine: API keys.
    """

    database: DatabaseConfig = DatabaseConfig()
    engine: EngineConfig = EngineConfig()


@lru_cache
def get_settings() -> Settings:
    """Retrieve application settings.

    Returns:
        Application settings.
    """
    return Settings()
