from pathlib import Path

from fastapi import Depends, FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from groq import AsyncGroq
from loguru import logger
from psycopg import AsyncConnection
from pydantic import UUID4
from pydantic_ai import Agent

from app.api.dependencies import (
    get_agent,
    get_agent_dependencies,
    get_conversation_id,
    get_db_conn,
    get_groq_client,
    get_tts_handler,
)
from app.api.lifespan import app_lifespan as lifespan
from app.database.actions import get_conversation_history, store_message
from app.engine.speech_to_text import transcribe_audio_data
from app.engine.text_to_speech import TextToSpeech
from app.services.agent import Dependencies
from app.services.utils import format_messages_for_agent

app = FastAPI(title="Voice to Voice Demo", lifespan=lifespan)


@app.get("/")
async def get():
    """
    Serves the main HTML page of the application.

    Returns:
        HTMLResponse containing the content of 'ui_draft' file.
    """
    with Path("sample_ui.html").open("r") as file:
        return HTMLResponse(file.read())


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        A dictionary indicating the status of the application.
    """
    return {"status": "ok"}


@app.websocket("/voice_stream")
async def voice_to_voice(
    websocket: WebSocket,
    conversation_id: UUID4 = Depends(get_conversation_id),
    db_conn: AsyncConnection = Depends(get_db_conn),
    groq_client: AsyncGroq = Depends(get_groq_client),
    agent: Agent[Dependencies] = Depends(get_agent),
    agent_deps: Dependencies = Depends(get_agent_dependencies),
    tts_handler: TextToSpeech = Depends(get_tts_handler),
):
    """
    WebSocket endpoint for voice-to-voice communication.

    - Receives audio bytes from the client
    - Transcribes the audio to text
    - generates a response using the language model agent
    - converts the response text to speech, and streams the audio bytes back to the client.

    Args:
        websocket: WebSocket connection.
        conversation_id: Unique identifier for the conversation (dependency).
        db_conn: Asynchronous database connection (dependency).
        groq_client: Groq API client for transcription (dependency).
        agent: Language model agent for generating responses (dependency).
        agent_deps: Dependencies for the agent (dependency).
        tts_handler: Text-to-Speech handler for converting text to audio (dependency).
    """
    await websocket.accept()
    logger.info(f"New websocket connection for conversation {conversation_id}")

    async for incoming_audio_bytes in websocket.iter_bytes():
        # Step 1: Transcribe the incoming audio
        logger.info("Starting transcription process")
        transcription = await transcribe_audio_data(
            audio_data=incoming_audio_bytes,
            api_client=groq_client,
            model_name="whisper-large-v3-turbo",
        )
        logger.debug("Transcription: {t}", t=transcription)

        # Step 2: Store the user's message
        await store_message(
            conn=db_conn,
            conversation_id=conversation_id,
            sender="user",
            content=transcription,
        )

        # Step 3: Retrieve the conversation history
        conversation_history = await get_conversation_history(
            conn=db_conn, conversation_id=conversation_id
        )

        # Step 4: Prepare the messages for the agent
        agent_messages = format_messages_for_agent(
            conversation_history=conversation_history
        )

        # Step 5: Generate the agent's response
        logger.info("Stating generation process")
        generation = ""
        async with tts_handler:
            async with agent.run_stream(
                user_prompt=transcription,
                message_history=agent_messages,
                deps=agent_deps,
            ) as result:
                async for message in result.stream_text(delta=True):
                    logger.debug("Delta: {m}", m=message)
                    generation += message

                    # Stream the audio back to the client
                    async for audio_chunk in tts_handler.feed(text=message):
                        await websocket.send_bytes(data=audio_chunk)

            # Flush any remaining audio chunks
            async for audio_chunk in tts_handler.flush():
                await websocket.send_bytes(data=audio_chunk)

        # Step 6: Store the agent's response
        await store_message(
            conn=db_conn,
            conversation_id=conversation_id,
            sender="agent",
            content=generation,
        )
