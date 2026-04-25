from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import AiAnalysis, Client, Incident, IncidentPhoto, User
from app.shared.dependencies.auth import is_workshop_user

MOCK_VISION_MODEL_VERSION = "mock-vision-v1"
DEFAULT_PRIORITY_LEVEL = "media"


def build_mock_classification(photo: IncidentPhoto) -> str:
    photo_context = f"{photo.file_url} {photo.format or ''}".lower()

    if any(keyword in photo_context for keyword in ("llanta", "neumatic", "tire", "rueda", "pinch")):
        return "neumatico"
    if any(keyword in photo_context for keyword in ("bateria", "electr", "cable", "luz", "alternador")):
        return "problema electrico"
    if any(keyword in photo_context for keyword in ("golpe", "choque", "aboll", "paracho", "puerta", "exterior")):
        return "danio exterior"
    if any(keyword in photo_context for keyword in ("motor", "mecan", "aceite", "humo", "radiador")):
        return "falla mecanica"

    return "incidente no clasificado"


def classify_incident_photo(db: Session, incident_id: int, current_user: User) -> dict:
    incident = db.scalar(
        select(Incident)
        .options(selectinload(Incident.photos))
        .where(Incident.id_incident == incident_id)
    )
    if not incident:
        raise LookupError("Incidente no encontrado")

    current_client = db.get(Client, current_user.id_user)
    can_access_as_client = current_client is not None and incident.id_client == current_client.id_user
    can_access_as_workshop = is_workshop_user(current_user, db)

    if not can_access_as_client and not can_access_as_workshop:
        raise PermissionError("No tienes permisos para ejecutar la clasificacion de este incidente")

    if not incident.photos:
        raise ValueError("El incidente no tiene fotos asociadas para clasificar")

    latest_photo = max(
        incident.photos,
        key=lambda photo: (
            photo.created_at,
            photo.id_photo,
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

    ai_analysis.classification = build_mock_classification(latest_photo)
    ai_analysis.model_version = MOCK_VISION_MODEL_VERSION

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo guardar la clasificacion del incidente en ai_analyses") from exc

    db.refresh(ai_analysis)

    return {
        "id_ai_analysis": ai_analysis.id_ai_analysis,
        "id_incident": ai_analysis.id_incident,
        "classification": ai_analysis.classification,
        "model_version": ai_analysis.model_version,
        "created_at": ai_analysis.created_at,
        "source_photo": latest_photo,
    }
