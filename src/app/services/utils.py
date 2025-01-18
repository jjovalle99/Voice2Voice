from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)


def format_messages_for_agent(
    conversation_history: list[dict[str, str]],
) -> list[ModelMessage]:
    """
    Format the conversation history for the PydanticAI agent.

    Args:
        conversation_history: List of dictionaries containing the conversation history.

    Returns:
        List of ModelMessage objects containing the conversation history.
    """
    messages: list[ModelMessage] = []
    for msg in conversation_history:
        if msg["sender"] == "user":
            messages.append(
                ModelRequest(parts=[UserPromptPart(content=msg["content"])])
            )
        elif msg["sender"] == "agent":
            messages.append(
                ModelResponse(parts=[TextPart(content=msg["content"])])
            )
        else:
            continue
    return messages
