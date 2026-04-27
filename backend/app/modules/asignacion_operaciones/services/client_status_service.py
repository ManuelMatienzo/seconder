from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Assignment, Incident


def get_client_incident_status(db: Session, incident: Incident) -> dict:
    assignment = db.scalar(
        select(Assignment)
        .options(
            joinedload(Assignment.workshop),
            joinedload(Assignment.technician),
        )
        .where(Assignment.id_incident == incident.id_incident)
        .order_by(Assignment.id_assignment.desc())
    )

    ai_analysis = incident.ai_analysis

    return {
        "id_incident": incident.id_incident,
        "incident_status": incident.status,
        "assignment_status": assignment.status if assignment else None,
        "priority_level": ai_analysis.priority_level if ai_analysis else None,
        "estimated_time_min": assignment.estimated_time_min if assignment else None,
        "distance_km": assignment.distance_km if assignment else None,
        "workshop": {
            "id_workshop": assignment.workshop.id_user,
            "workshop_name": assignment.workshop.workshop_name,
            "phone": assignment.workshop.phone,
        }
        if assignment and assignment.workshop
        else None,
        "technician": {
            "id_technician": assignment.technician.id_technician,
            "name": assignment.technician.name,
            "phone": assignment.technician.phone,
            "specialty": assignment.technician.specialty,
        }
        if assignment and assignment.technician
        else None,
    }
