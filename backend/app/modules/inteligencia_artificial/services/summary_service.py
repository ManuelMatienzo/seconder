from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AiAnalysis, Client, Incident, User
from app.shared.dependencies.auth import is_workshop_user

DEFAULT_PRIORITY_LEVEL = "media"
SUMMARY_MODEL_VERSION = "summary-rules-v1"


def truncate_text(value: str, max_length: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3].rstrip() + "..."


def build_vehicle_fragment(incident: Incident) -> tuple[str, bool]:
    vehicle = incident.vehicle
    if not vehicle:
        return "Vehiculo asociado no disponible.", False

    details: list[str] = []
    brand_model = " ".join(part for part in (vehicle.brand, vehicle.model) if part)
    if brand_model:
        details.append(brand_model)
    if vehicle.plate:
        details.append(f"placa {vehicle.plate}")
    if vehicle.color:
        details.append(f"color {vehicle.color}")
    if vehicle.type:
        details.append(f"tipo {vehicle.type}")
    if vehicle.year:
        details.append(f"anio {vehicle.year}")

    if not details:
        return "Vehiculo asociado con datos minimos.", True

    return "Vehiculo asociado: " + ", ".join(details) + ".", True


def build_structured_summary(incident: Incident, ai_analysis: AiAnalysis) -> tuple[str, dict[str, bool]]:
    sources_used = {
        "description_text": bool(incident.description_text),
        "audio_transcription": bool(ai_analysis.audio_transcription),
        "classification": bool(ai_analysis.classification),
        "priority_level": bool(ai_analysis.priority_level),
        "vehicle_data": bool(incident.vehicle),
    }

    parts = [f"Incidente {incident.status} reportado."]

    vehicle_fragment, vehicle_used = build_vehicle_fragment(incident)
    sources_used["vehicle_data"] = vehicle_used
    parts.append(vehicle_fragment)

    if incident.description_text:
        parts.append(f"Descripcion inicial: '{truncate_text(incident.description_text)}'.")

    if ai_analysis.classification:
        parts.append(f"Clasificacion detectada: {ai_analysis.classification}.")

    priority_level = ai_analysis.priority_level or DEFAULT_PRIORITY_LEVEL
    if ai_analysis.severity_score is not None:
        severity_display = int(ai_analysis.severity_score)
        parts.append(f"Prioridad estimada: {priority_level} con severidad {severity_display}/100.")
    else:
        parts.append(f"Prioridad estimada: {priority_level}.")

    parts.append(
        "Ubicacion registrada: "
        f"lat {incident.latitude:.7f}, lon {incident.longitude:.7f}."
    )

    if ai_analysis.audio_transcription:
        parts.append(f"Transcripcion relevante del audio: {truncate_text(ai_analysis.audio_transcription)}.")

    return " ".join(parts), sources_used


def generate_incident_summary(db: Session, incident_id: int, current_user: User) -> dict:
    incident = db.scalar(
        select(Incident)
        .options(joinedload(Incident.ai_analysis), joinedload(Incident.vehicle))
        .where(Incident.id_incident == incident_id)
    )
    if not incident:
        raise LookupError("Incidente no encontrado")

    current_client = db.get(Client, current_user.id_user)
    can_access_as_client = current_client is not None and incident.id_client == current_client.id_user
    can_access_as_workshop = is_workshop_user(current_user, db)

    if not can_access_as_client and not can_access_as_workshop:
        raise PermissionError("No tienes permisos para generar la ficha resumen de este incidente")

    ai_analysis = incident.ai_analysis
    if not ai_analysis:
        ai_analysis = AiAnalysis(
            id_incident=incident_id,
            priority_level=DEFAULT_PRIORITY_LEVEL,
        )
        db.add(ai_analysis)

    structured_summary, sources_used = build_structured_summary(incident, ai_analysis)
    ai_analysis.structured_summary = structured_summary
    ai_analysis.model_version = SUMMARY_MODEL_VERSION

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo guardar la ficha resumen del incidente en ai_analyses") from exc

    db.refresh(ai_analysis)

    return {
        "id_ai_analysis": ai_analysis.id_ai_analysis,
        "id_incident": ai_analysis.id_incident,
        "structured_summary": ai_analysis.structured_summary,
        "model_version": ai_analysis.model_version or SUMMARY_MODEL_VERSION,
        "sources_used": sources_used,
    }
