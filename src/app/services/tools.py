from typing import Literal

from loguru import logger
from pydantic_ai import RunContext

from app.services.agent import Dependencies

type AvailableCities = Literal["Paris", "Madrid", "London"]


async def get_weather(
    ctx: RunContext[Dependencies], city: AvailableCities
) -> str:
    """
    Fetch the weather for a given city. Only Paris, Madrid and London are available.

    Args:
        ctx: The context of the current run.
        city: The city to get the weather for.

    Returns:
        A string with the weather information.
    """
    logger.info(f"Getting weather for {city}")
    url = "http://api.weatherstack.com/current"
    params = {
        "access_key": ctx.deps.settings.engine.weatherstack_api_key,
        "query": city,
    }

    async with ctx.deps.session.get(url=url, params=params) as response:
        data = await response.json()
        observation_time = data.get("current").get("observation_time")
        temperature = data.get("current").get("temperature")
        weather_descriptions = data.get("current").get("weather_descriptions")
        return f"At {observation_time}, the temperature in {city} is {temperature}°C. The weather is {weather_descriptions[0].lower()}"
