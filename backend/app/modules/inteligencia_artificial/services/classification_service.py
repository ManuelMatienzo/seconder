from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models import AiAnalysis, Client, Incident, IncidentPhoto, User
from app.modules.inteligencia_artificial.providers.vision import build_mock_classification, classify_image_with_groq_vision
from app.modules.inteligencia_artificial.providers.vision.groq_vision import GroqVisionError
from app.shared.dependencies.auth import is_workshop_user

MOCK_VISION_MODEL_VERSION = "mock-vision-v1"
DEFAULT_PRIORITY_LEVEL = "media"


class ClassificationProviderError(RuntimeError):
    pass


def classify_with_selected_provider(photo: IncidentPhoto) -> tuple[str, str]:
    provider = settings.CLASSIFICATION_PROVIDER.strip().lower()

    if provider != "groq":
        return build_mock_classification(photo), MOCK_VISION_MODEL_VERSION

    try:
        return classify_image_with_groq_vision(photo.file_url)
    except GroqVisionError as exc:
        if settings.ALLOW_CLASSIFICATION_FALLBACK:
            return build_mock_classification(photo), MOCK_VISION_MODEL_VERSION
        raise ClassificationProviderError(str(exc)) from exc


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

    classification, model_version = classify_with_selected_provider(latest_photo)
    ai_analysis.classification = classification
    ai_analysis.model_version = model_version

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
