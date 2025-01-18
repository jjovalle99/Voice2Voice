from typing import AsyncIterator, cast
from uuid import uuid4

from fastapi import WebSocket
from groq import AsyncGroq
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from pydantic import UUID4
from pydantic_ai import Agent

from app.config.settings import get_settings
from app.engine.text_to_speech import TextToSpeech
from app.services.agent import Dependencies


async def get_db_conn(websocket: WebSocket) -> AsyncIterator[AsyncConnection]:
    """
    Gets a connection to the database using the connection pool.

    Args:
        websocket: WebSocket connection.

    Yields:
        Connection to the database.
    """
    db_pool = cast(AsyncConnectionPool, websocket.state.pool)
    async with db_pool.connection() as conn:
        yield conn


async def get_conversation_id() -> UUID4:
    """
    Creates a new conversation ID.

    Returns:
        Conversation ID.
    """
    return uuid4()


async def get_agent_dependencies(websocket: WebSocket) -> Dependencies:
    """
    Gets the dependencies for the PydanticAI Agent.

    Args:
        websocket: WebSocket connection.

    Returns:
        Dependencies instance.
    """
    return Dependencies(
        settings=get_settings(),
        session=websocket.state.aiohttp_session,
    )


async def get_groq_client(websocket: WebSocket) -> AsyncGroq:
    """
    Gets a client for interacting with Groq API.

    Args:
        websocket: WebSocket connection.

    Returns:
        Client for interacting with Groq API
    """
    return websocket.state.groq_client


async def get_agent(websocket: WebSocket) -> Agent:
    """
    Gets a PydanticAI Agent that uses Groq models.

    Args:
        websocket: WebSocket connection.

    Returns:
        PydanticAI Agent that uses Groq models.
    """
    return websocket.state.groq_agent


async def get_tts_handler(websocket: WebSocket) -> TextToSpeech:
    """
    Gets a handler for text-to-speech conversion.

    Args:
        websocket: WebSocket connection.

    Returns:
        Handler for text-to-speech conversion.
    """
    return TextToSpeech(
        client=websocket.state.openai_client,
        model_name="tts-1",
        response_format="aac",
    )
