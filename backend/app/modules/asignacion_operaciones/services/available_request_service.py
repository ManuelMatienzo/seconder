from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AiAnalysis, Incident, Vehicle


def list_available_requests(db: Session) -> list[dict]:
    stmt = (
        select(Incident, Vehicle, AiAnalysis)
        .join(Vehicle, Vehicle.id_vehicle == Incident.id_vehicle)
        .outerjoin(AiAnalysis, AiAnalysis.id_incident == Incident.id_incident)
        .where(Incident.status == "pendiente")
        .order_by(Incident.created_at.desc())
    )

    results = db.execute(stmt).all()
    items: list[dict] = []

    for incident, vehicle, ai_analysis in results:
        items.append(
            {
                "id_incident": incident.id_incident,
                "id_client": incident.id_client,
                "id_vehicle": incident.id_vehicle,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "description_text": incident.description_text,
                "status": incident.status,
                "created_at": incident.created_at,
                "updated_at": incident.updated_at,
                "vehicle": {
                    "id_vehicle": vehicle.id_vehicle,
                    "plate": vehicle.plate,
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
