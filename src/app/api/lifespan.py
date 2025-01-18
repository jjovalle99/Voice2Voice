from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

import aiohttp
from fastapi import FastAPI
from groq import AsyncGroq
from loguru import logger
from openai import AsyncOpenAI
from psycopg_pool import AsyncConnectionPool
from pydantic_ai import Agent, Tool

from app.config.settings import get_settings
from app.database.actions import create_main_table
from app.database.connection import create_db_connection_pool
from app.services.agent import Dependencies, create_groq_agent
from app.services.factories import (
    create_aiohttp_session,
    create_groq_client,
    create_groq_model,
    create_openai_client,
)
from app.services.tools import get_weather


class State(TypedDict):
    """Application state container for shared resources.

    Attributes:
        pool: Database connection pool for async operations.
        aiohttp_session: Client session for making HTTP requests.
        groq_client: Client for interacting with Groq API.
        openai_client: Client for interacting with OpenAI API.
        groq_agent: PydanticAI Agent that uses Groq models.
    """

    pool: AsyncConnectionPool
    aiohttp_session: aiohttp.ClientSession
    groq_client: AsyncGroq
    openai_client: AsyncOpenAI
    groq_agent: Agent[Dependencies]


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[State]:
    """Manages application lifecycle and shared resources.

    Handles initialization and cleanup of application-wide resources
    during startup and shutdown phases.

    Args:
        app: FastAPI application instance.

    Yields:
        Application state containing shared resources.
    """
    settings = get_settings()
    aiohttp_session = create_aiohttp_session()
    pool = create_db_connection_pool(settings=settings)
    openai_client = create_openai_client(settings=settings)
    groq_client = create_groq_client(settings=settings)
    _groq_model = create_groq_model(groq_client=groq_client)
    groq_agent = create_groq_agent(
        groq_model=_groq_model,
        tools=[Tool(function=get_weather, takes_ctx=True)],
        system_prompt=(
            "You are a helpful assistant. "
            "You interact with the user in a natural way. "
            "You should use `get_weather` ONLY to provide weather information."
        ),
    )

    logger.info("Opening database connection pool")
    await pool.open()
    await create_main_table(pool)

    yield {
        "pool": pool,
        "aiohttp_session": aiohttp_session,
        "openai_client": openai_client,
        "groq_client": groq_client,
        "groq_agent": groq_agent,
    }

    logger.info("Closing aiohttp session")
    await aiohttp_session.close()

    logger.info("Closing database connection pool")
    await pool.close()

    logger.info("Closing OpenAI client")
    await openai_client.close()

    logger.info("Closing Groq client")
    await groq_client.close()
