from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Assignment, Incident, Workshop


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

    workshop = assignment.workshop if assignment and assignment.workshop else None
    if workshop is None and incident.assigned_workshop_id is not None:
        workshop = db.get(Workshop, incident.assigned_workshop_id)

    return {
        "id_incident": incident.id_incident,
        "incident_status": incident.status,
        "assignment_status": assignment.status if assignment else None,
        "priority_level": ai_analysis.priority_level if ai_analysis else None,
        "estimated_time_min": assignment.estimated_time_min if assignment else None,
        "distance_km": assignment.distance_km if assignment else None,
        "workshop": {
            "id_workshop": workshop.id_user,
            "workshop_name": workshop.workshop_name,
            "phone": workshop.phone,
        }
        if workshop
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


def update_client_incident_status(db: Session, incident: Incident, status: str) -> None:
    normalized_status = status.lower()
    if normalized_status not in {"finalizado", "cancelado"}:
        raise ValueError("El cliente solo puede marcar el incidente como finalizado o cancelado.")

    # Evitar violar el constraint de estados en incidentes.
    # 'finalizado' es solo para el assignment (flujo post-pago).
    if normalized_status == "finalizado":
        incident.status = "atendido"
    else:
        incident.status = normalized_status
    
    # Si hay un assignment activo, deberia actualizarse tambien
    assignment = db.scalar(
        select(Assignment)
        .where(Assignment.id_incident == incident.id_incident)
        .order_by(Assignment.id_assignment.desc())
    )
    
    if assignment:
        if normalized_status != "finalizado" and assignment.status not in {"cancelado", "completado", "rechazado"}:
            assignment.status = "cancelado" if normalized_status == "cancelado" else normalized_status
        
    db.commit()
