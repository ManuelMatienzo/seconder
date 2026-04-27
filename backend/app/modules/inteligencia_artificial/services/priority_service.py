from decimal import Decimal
import unicodedata

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AiAnalysis, Client, Incident, User
from app.shared.dependencies.auth import is_workshop_user

DEFAULT_PRIORITY_LEVEL = "media"
PRIORITY_MODEL_VERSION = "priority-rules-v1"


def normalize_text(value: str | None) -> str:
    if not value:
        return ""

    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def has_any_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def infer_priority_and_score(
    description_text: str | None,
    audio_transcription: str | None,
    classification: str | None,
) -> tuple[str, int]:
    combined_text = " ".join(
        part for part in (normalize_text(description_text), normalize_text(audio_transcription), normalize_text(classification)) if part
    )
    normalized_classification = normalize_text(classification)

    score = 35

    if normalized_classification == "neumatico":
        score = max(score, 35)
    elif normalized_classification == "danio exterior":
        score = max(score, 45)
    elif normalized_classification == "falla mecanica":
        score = max(score, 55)
    elif normalized_classification == "problema electrico":
        score = max(score, 60)

    critical_keywords = ("incendio", "fuego", "explosion", "explosiono", "herido", "volco", "volcada", "atrapado")
    high_keywords = ("accidente", "choque", "humo", "no responde", "motor detenido", "freno", "sin frenos")
    medium_keywords = ("no enciende", "bateria", "motor", "radiador", "sobrecalent", "aceite", "electric")
    low_keywords = ("llanta", "pinchazo", "neumatic", "golpe leve", "raspon")

    if has_any_keyword(combined_text, critical_keywords):
        score = max(score, 92)
    elif has_any_keyword(combined_text, high_keywords):
        score = max(score, 72)
    elif has_any_keyword(combined_text, medium_keywords):
        score = max(score, 52)
    elif has_any_keyword(combined_text, low_keywords):
        score = max(score, 28)

    if normalized_classification == "problema electrico" and has_any_keyword(combined_text, ("humo", "chispa", "olor a quemado")):
        score = max(score, 88)

    if normalized_classification == "falla mecanica" and has_any_keyword(combined_text, ("no enciende", "motor", "detenido")):
        score = max(score, 68)

    if normalized_classification == "danio exterior" and has_any_keyword(combined_text, ("choque", "accidente", "volco")):
        score = max(score, 82)

    if score >= 86:
        return "critica", score
    if score >= 61:
        return "alta", score
    if score >= 31:
        return "media", score
    return "baja", score


def detect_incident_priority(db: Session, incident_id: int, current_user: User) -> dict:
    incident = db.scalar(
        select(Incident)
        .options(joinedload(Incident.ai_analysis))
        .where(Incident.id_incident == incident_id)
    )
    if not incident:
        raise LookupError("Incidente no encontrado")

    current_client = db.get(Client, current_user.id_user)
    can_access_as_client = current_client is not None and incident.id_client == current_client.id_user
    can_access_as_workshop = is_workshop_user(current_user, db)

    if not can_access_as_client and not can_access_as_workshop:
        raise PermissionError("No tienes permisos para detectar la prioridad de este incidente")

    ai_analysis = incident.ai_analysis
    if not ai_analysis:
        ai_analysis = AiAnalysis(
            id_incident=incident_id,
            priority_level=DEFAULT_PRIORITY_LEVEL,
        )
        db.add(ai_analysis)

    priority_level, severity_score = infer_priority_and_score(
        incident.description_text,
        ai_analysis.audio_transcription if ai_analysis else None,
        ai_analysis.classification if ai_analysis else None,
    )

    ai_analysis.priority_level = priority_level
    ai_analysis.severity_score = Decimal(severity_score)
    ai_analysis.model_version = PRIORITY_MODEL_VERSION

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo guardar la prioridad del incidente en ai_analyses") from exc

    db.refresh(ai_analysis)

    return {
        "id_ai_analysis": ai_analysis.id_ai_analysis,
        "id_incident": ai_analysis.id_incident,
        "priority_level": ai_analysis.priority_level,
        "severity_score": int(ai_analysis.severity_score or 0),
        "model_version": ai_analysis.model_version or PRIORITY_MODEL_VERSION,
        "signals_used": {
            "description_text": incident.description_text,
            "classification": ai_analysis.classification,
            "audio_transcription_used": bool(ai_analysis.audio_transcription),
        },
    }
