from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.inteligencia_artificial.models.ai_analysis import AiAnalysis
from app.modules.reporte_emergencias.models.incident import Incident
from app.modules.gestion_usuarios.models.vehicle import Vehicle
from app.modules.gestion_usuarios.models.user import User
from app.modules.reporte_emergencias.models.incident_photo import IncidentPhoto
from app.modules.reporte_emergencias.models.incident_audio import IncidentAudio
from app.modules.gestion_usuarios.models.client import Client


def list_available_requests(db: Session, workshop_id: int | None = None) -> list[dict]:
    stmt = (
        select(Incident)
        .options(
            joinedload(Incident.vehicle),
            joinedload(Incident.client).joinedload(Client.user),
            joinedload(Incident.ai_analysis),
            joinedload(Incident.photos),
            joinedload(Incident.audios),
        )
        .where(Incident.status == "pendiente")
        .order_by(Incident.created_at.desc())
    )

    # Si se proporciona workshop_id, filtrar solo los incidentes asignados a ese taller
    if workshop_id is not None:
        stmt = stmt.where(Incident.assigned_workshop_id == workshop_id)

    incidents = db.scalars(stmt).unique().all()
    items: list[dict] = []

    for incident in incidents:
        vehicle = incident.vehicle
        client_obj = incident.client
        user = client_obj.user if client_obj else None
        ai_analysis = incident.ai_analysis
        
        # Get the most recent photo and audio
        latest_photo = max(incident.photos, key=lambda p: p.created_at) if incident.photos else None
        latest_audio = max(incident.audios, key=lambda a: a.created_at) if incident.audios else None

        items.append(
            {
                "id_incident": incident.id_incident,
                "id_client": incident.id_client,
                "id_vehicle": incident.id_vehicle,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "description_text": incident.description_text,
                "status": incident.status,
                "assigned_workshop_id": incident.assigned_workshop_id,
                "created_at": incident.created_at,
                "updated_at": incident.updated_at,
                "photo_url": latest_photo.file_url if latest_photo else None,
                "audio_url": latest_audio.file_url if latest_audio else None,
                "client": {
                    "id_client": user.id_user,
                    "name": user.name,
                    "phone": user.phone,
                }
                if user
                else None,
                "vehicle": {
                    "id_vehicle": vehicle.id_vehicle,
                    "license_plate": vehicle.plate,
                    "brand": vehicle.brand,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "color": vehicle.color,
                    "type": vehicle.type,
                }
                if vehicle
                else None,
                "ai_analysis": {
                    "audio_transcription": ai_analysis.audio_transcription,
                    "classification": ai_analysis.classification,
                    "priority_level": ai_analysis.priority_level,
                    "structured_summary": ai_analysis.structured_summary,
                }
                if ai_analysis
                else None,
            }
        )

    return items
