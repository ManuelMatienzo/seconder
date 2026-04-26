import os
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models import AiAnalysis, Client, Incident, IncidentAudio, User
from app.modules.inteligencia_artificial.providers.stt import build_mock_transcription, transcribe_file_with_groq
from app.modules.inteligencia_artificial.providers.stt.groq_stt import GroqTranscriptionError
from app.shared.dependencies.auth import is_workshop_user

MOCK_MODEL_VERSION = "mock-v1"
DEFAULT_PRIORITY_LEVEL = "media"


class TranscriptionProviderError(RuntimeError):
    pass


def download_audio_temporarily(audio: IncidentAudio) -> str:
    parsed_url = urlparse(audio.file_url)
    suffix = os.path.splitext(parsed_url.path)[1]
    if not suffix:
        suffix = f".{audio.format}" if audio.format else ".bin"

    try:
        with urlopen(audio.file_url, timeout=30) as response:
            audio_bytes = response.read()
    except Exception as exc:
        raise TranscriptionProviderError("No se pudo descargar el audio asociado al incidente") from exc

    if not audio_bytes:
        raise TranscriptionProviderError("El archivo de audio descargado esta vacio")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp_file.write(audio_bytes)
        temp_file.flush()
    finally:
        temp_file.close()

    return temp_file.name


def transcribe_with_selected_provider(incident: Incident, audio: IncidentAudio) -> tuple[str, str]:
    provider = settings.TRANSCRIPTION_PROVIDER.strip().lower()

    if provider != "groq":
        return build_mock_transcription(incident, audio), MOCK_MODEL_VERSION

    local_audio_path = download_audio_temporarily(audio)
    try:
        return transcribe_file_with_groq(local_audio_path)
    except GroqTranscriptionError as exc:
        if settings.ALLOW_TRANSCRIPTION_FALLBACK:
            return build_mock_transcription(incident, audio), MOCK_MODEL_VERSION
        raise TranscriptionProviderError(str(exc)) from exc
    finally:
        try:
            os.remove(local_audio_path)
        except OSError:
            pass


def transcribe_incident_audio(db: Session, incident_id: int, current_user: User) -> dict:
    incident = db.scalar(
        select(Incident)
        .options(selectinload(Incident.audios))
        .where(Incident.id_incident == incident_id)
    )
    if not incident:
        raise LookupError("Incidente no encontrado")

    current_client = db.get(Client, current_user.id_user)
    can_access_as_client = current_client is not None and incident.id_client == current_client.id_user
    can_access_as_workshop = is_workshop_user(current_user, db)

    if not can_access_as_client and not can_access_as_workshop:
        raise PermissionError("No tienes permisos para ejecutar la transcripcion de este incidente")

    if not incident.audios:
        raise ValueError("El incidente no tiene audios asociados para transcribir")

    latest_audio = max(
        incident.audios,
        key=lambda audio: (
            audio.created_at,
            audio.id_audio,
        ),
    )

    ai_analysis = db.scalar(
        select(AiAnalysis)
        .where(AiAnalysis.id_incident == incident_id)
        .order_by(AiAnalysis.created_at.desc(), AiAnalysis.id_ai_analysis.desc())
    )

    if not ai_analysis:
        ai_analysis = AiAnalysis(
            id_incident=incident_id,
            priority_level=DEFAULT_PRIORITY_LEVEL,
        )
        db.add(ai_analysis)

    transcription_text, model_version = transcribe_with_selected_provider(incident, latest_audio)
    ai_analysis.audio_transcription = transcription_text
    ai_analysis.model_version = model_version

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo guardar la transcripcion del incidente en ai_analyses") from exc

    db.refresh(ai_analysis)

    return {
        "id_ai_analysis": ai_analysis.id_ai_analysis,
        "id_incident": ai_analysis.id_incident,
        "audio_transcription": ai_analysis.audio_transcription,
        "model_version": ai_analysis.model_version,
        "created_at": ai_analysis.created_at,
        "source_audio": latest_audio,
    }
