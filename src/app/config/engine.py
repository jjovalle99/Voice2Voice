import os

from pydantic_settings import BaseSettings


class EngineConfig(BaseSettings):
    """
    API keys for external services.

    Attributes:
        groq_api_key: Groq API authentication key.
        openai_api_key: OpenAI API authentication key.
        weatherstack_api_key: Weather Stack API authentication key.
    """

    groq_api_key: str = os.environ["GROQ_API_KEY"]
    openai_api_key: str = os.environ["OPENAI_API_KEY"]
    weatherstack_api_key: str = os.environ["WEATHERSTACK_API_KEY"]
