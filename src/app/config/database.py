import os

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration.

    Attributes:
        name: Database name.
        user: Database user.
        password: Database password.
        host: Database host.
        port: Database port.
    """

    name: str = os.environ["DB_NAME"]
    user: str = os.environ["DB_USER"]
    password: str = os.environ["DB_PASSWORD"]
    host: str = os.environ["DB_HOST"]
    port: str = os.environ["DB_PORT"]

    @property
    def conninfo(self) -> str:
        """PostgreSQL connection string in libpq format."""
        return (
            f"dbname={self.name} "
            f"user={self.user} "
            f"password={self.password} "
            f"host={self.host} "
            f"port={self.port}"
        )
