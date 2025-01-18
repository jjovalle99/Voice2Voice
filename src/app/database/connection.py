from psycopg_pool import AsyncConnectionPool

from app.config.settings import Settings


def create_db_connection_pool(
    settings: Settings,
) -> AsyncConnectionPool:
    """
    Create a connection pool to the database. It is closed by default.

    Args:
        settings: Application settings

    Returns:
        Connection pool to the database.
    """
    return AsyncConnectionPool(conninfo=settings.database.conninfo, open=False)
