from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import AiAnalysis, Client, Incident, IncidentAudio, User
from app.shared.dependencies.auth import is_workshop_user

MOCK_MODEL_VERSION = "mock-v1"
DEFAULT_PRIORITY_LEVEL = "media"


def build_mock_transcription(incident: Incident, audio: IncidentAudio) -> str:
    audio_format = audio.format or "desconocido"
    duration = f"{audio.duration_seconds} segundos" if audio.duration_seconds is not None else "duracion no especificada"
    return (
        f"Transcripcion simulada del incidente {incident.id_incident}. "
        f"Audio {audio.id_audio} en formato {audio_format}, {duration}. "
        f"Fuente registrada: {audio.file_url}."
    )


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

    ai_analysis.audio_transcription = build_mock_transcription(incident, latest_audio)
    ai_analysis.model_version = MOCK_MODEL_VERSION

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
