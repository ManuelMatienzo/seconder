from pathlib import Path

from app.core.config import settings


class GroqTranscriptionError(RuntimeError):
    pass


def transcribe_file_with_groq(file_path: str) -> tuple[str, str]:
    try:
        from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
    except ImportError as exc:
        raise GroqTranscriptionError("La dependencia 'openai' no esta instalada para usar Groq STT") from exc

    if not settings.GROQ_API_KEY:
        raise GroqTranscriptionError("GROQ_API_KEY no esta configurado")

    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
        timeout=60.0,
    )

    filename = Path(file_path).name

    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(filename, audio_file.read()),
                model=settings.GROQ_STT_MODEL,
                response_format="json",
                temperature=0.0,
            )
    except (APIConnectionError, APITimeoutError) as exc:
        raise GroqTranscriptionError("No se pudo conectar con Groq Speech-to-Text") from exc
    except APIStatusError as exc:
        raise GroqTranscriptionError(f"Groq Speech-to-Text respondio con error HTTP {exc.status_code}") from exc
    except OSError as exc:
        raise GroqTranscriptionError("No se pudo abrir el archivo de audio para enviarlo a Groq") from exc
    except Exception as exc:
        raise GroqTranscriptionError("Ocurrio un error inesperado al transcribir con Groq") from exc

    text = getattr(transcription, "text", None)
    if not text and isinstance(transcription, dict):
        text = transcription.get("text")

    if not text:
        raise GroqTranscriptionError("Groq no devolvio texto transcrito")

    return text.strip(), f"groq-{settings.GROQ_STT_MODEL}"
