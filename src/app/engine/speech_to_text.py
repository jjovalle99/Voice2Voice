from io import BytesIO

from groq import AsyncGroq


async def transcribe_audio_data(
    audio_data: bytes,
    api_client: AsyncGroq,
    model_name: str,
    temperature: float = 0.0,
    language: str = "en",
) -> str:
    """
    Transcribe audio to text using the Groq model

    Args:
        audio_data: Audio data to transcribe
        api_client: Groq API client
        model_name: Name of the Groq model to use
        temperature: Temperature for sampling
        language: Language of the audio

    Returns:
        Transcribed text
    """
    with BytesIO(initial_bytes=audio_data) as audio_stream:
        audio_stream.name = "audio.wav"
        response = await api_client.audio.transcriptions.create(
            model=model_name,
            file=audio_stream,
            temperature=temperature,
            language=language,
        )
        text = response.text.strip()
        return text
