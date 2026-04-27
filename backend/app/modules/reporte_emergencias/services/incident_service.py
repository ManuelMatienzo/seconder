from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import Incident, IncidentAudio, IncidentPhoto, Vehicle
from app.modules.reporte_emergencias.schemas import (
    IncidentAudioCreateRequest,
    IncidentCreateRequest,
    IncidentDescriptionUpdateRequest,
    IncidentPhotoCreateRequest,
)
from app.services.ai_service import AIService


def create_incident(db: Session, client_id: int, data: IncidentCreateRequest) -> Incident:
    vehicle = db.get(Vehicle, data.id_vehicle)
    if not vehicle:
        raise LookupError("Vehiculo no encontrado")

    if vehicle.id_client != client_id:
        raise PermissionError("No tienes permisos para crear incidentes con ese vehiculo")

    incident = Incident(
        id_client=client_id,
        id_vehicle=data.id_vehicle,
        latitude=data.latitude,
        longitude=data.longitude,
        description_text=data.description_text,
        status="pendiente",
    )
    db.add(incident)
    db.flush()

    for photo in data.photos:
        db.add(
            IncidentPhoto(
                id_incident=incident.id_incident,
                file_url=photo.file_url,
                format=photo.format,
                size_kb=photo.size_kb,
            )
        )

    for audio in data.audios:
        db.add(
            IncidentAudio(
                id_incident=incident.id_incident,
                file_url=audio.file_url,
                format=audio.format,
                duration_seconds=audio.duration_seconds,
            )
        )

    try:
        db.flush()
        AIService().process_incident(db, incident)
        db.commit()
    except (IntegrityError, ValueError) as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el incidente con los datos enviados") from exc

    return get_incident_by_id(db, incident.id_incident) or incident


def get_incident_by_id(db: Session, incident_id: int) -> Incident | None:
    return db.scalar(
        select(Incident)
        .options(selectinload(Incident.photos), selectinload(Incident.audios))
        .where(Incident.id_incident == incident_id)
    )


def update_incident_description(
    db: Session,
    incident_id: int,
    data: IncidentDescriptionUpdateRequest,
) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise LookupError("Incidente no encontrado")

    incident.description_text = data.description_text
    db.commit()

    return get_incident_by_id(db, incident_id) or incident


def create_incident_photo(db: Session, data: IncidentPhotoCreateRequest) -> IncidentPhoto:
    photo = IncidentPhoto(
        id_incident=data.id_incident,
        file_url=data.file_url,
        format=data.format,
        size_kb=data.size_kb,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def create_incident_audio(db: Session, data: IncidentAudioCreateRequest) -> IncidentAudio:
    audio = IncidentAudio(
        id_incident=data.id_incident,
        file_url=data.file_url,
        format=data.format,
        duration_seconds=data.duration_seconds,
    )
    db.add(audio)
    db.commit()
    db.refresh(audio)
    return audio
