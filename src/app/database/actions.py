from loguru import logger
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from pydantic import UUID4


async def create_main_table(pool: AsyncConnectionPool) -> None:
    """
    Create the main table IF it does not exist.

    Args:
        pool: Connection pool to the database.
    """
    logger.info("Executing query to create the main table `messages`...")
    query = (
        "CREATE TABLE IF NOT EXISTS messages ("
        "id SERIAL PRIMARY KEY,"
        "conversation_id UUID NOT NULL,"
        "sender VARCHAR(10) NOT NULL,"
        "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "content TEXT NOT NULL"
        ");"
    )
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query=query)


async def store_message(
    conn: AsyncConnection,
    conversation_id: UUID4,
    sender: str,
    content: str,
) -> None:
    """
    Store a message in the database.

    Args:
        conn: Asynchronous database connection.
        conversation_id: Unique identifier for the conversation.
        sender: Sender of the message. (e.g., "user" or "agent")
        content: Content of the message.
    """
    query = "INSERT INTO messages (conversation_id, sender, content) VALUES (%s, %s, %s);"
    params = (conversation_id, sender, content)

    async with conn.cursor() as cur:
        await cur.execute(query=query, params=params)
        await conn.commit()


async def get_conversation_history(
    conn: AsyncConnection, conversation_id: UUID4
) -> list[dict[str, str]]:
    """
    Retrieve the conversation history for a given conversation.

    Args:
        conn: Asynchronous database connection.
        conversation_id: Unique identifier for the conversation.

    Returns:
        List of dictionaries containing the sender and content of each message.
    """
    query = (
        "SELECT sender, content "
        "FROM messages "
        "WHERE conversation_id = %s "
        "ORDER BY timestamp ASC;"
    )
    params = (conversation_id,)

    async with conn.cursor() as cur:
        await cur.execute(query=query, params=params)
        rows = await cur.fetchall()
        conversation_history = [
            {"sender": row[0], "content": row[1]} for row in rows
        ]
    return conversation_history
