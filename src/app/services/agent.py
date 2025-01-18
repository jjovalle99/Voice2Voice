from dataclasses import dataclass
from typing import Sequence

import aiohttp
from pydantic_ai import Agent, Tool
from pydantic_ai.models.groq import GroqModel

from app.config.settings import Settings


@dataclass
class Dependencies:
    settings: Settings
    session: aiohttp.ClientSession


def create_groq_agent(
    groq_model: GroqModel,
    tools: Sequence[Tool[Dependencies]],
    system_prompt: str,
) -> Agent[Dependencies]:
    """
    Creates a PydanticAI Agent that uses Groq models.

    Args:
        groq_model: Groq model for PydanticAI.

    Returns:
        PydanticAI Agent that uses Groq models.
    """

    return Agent(
        model=groq_model,
        deps_type=Dependencies,
        system_prompt=system_prompt,
        tools=tools,
    )
