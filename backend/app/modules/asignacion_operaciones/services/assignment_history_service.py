from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Assignment, Incident
from app.modules.asignacion_operaciones.schemas import AssignmentHistoryFilterParams

DEFAULT_HISTORY_STATUSES = ("completado", "cancelado", "rechazado")


def _base_history_query(workshop_id: int):
    return (
        select(Assignment)
        .options(
            joinedload(Assignment.incident).joinedload(Incident.vehicle),
            joinedload(Assignment.incident).joinedload(Incident.ai_analysis),
            joinedload(Assignment.technician),
        )
        .where(Assignment.id_workshop == workshop_id)
    )


def _apply_history_filters(stmt, filters: AssignmentHistoryFilterParams):
    if filters.status:
        stmt = stmt.where(Assignment.status == filters.status)
    else:
        stmt = stmt.where(Assignment.status.in_(DEFAULT_HISTORY_STATUSES))

    if filters.id_technician is not None:
        stmt = stmt.where(Assignment.id_technician == filters.id_technician)

    if filters.date_from is not None:
        stmt = stmt.where(Assignment.assigned_at >= datetime.combine(filters.date_from, time.min))

    if filters.date_to is not None:
        stmt = stmt.where(Assignment.assigned_at < datetime.combine(filters.date_to + timedelta(days=1), time.min))

    return stmt


def _serialize_history_item(assignment: Assignment) -> dict:
    incident = assignment.incident
    if incident is None or incident.vehicle is None:
        raise LookupError("El assignment no tiene incidente o vehiculo asociado valido")

    ai_analysis = incident.ai_analysis
    technician = assignment.technician

    return {
        "id_assignment": assignment.id_assignment,
        "id_incident": assignment.id_incident,
        "assignment_status": assignment.status,
        "incident_status": incident.status,
        "assigned_at": assignment.assigned_at,
        "accepted_at": assignment.accepted_at,
        "completed_at": assignment.completed_at,
        "estimated_time_min": assignment.estimated_time_min,
        "distance_km": assignment.distance_km,
        "service_price": assignment.service_price,
        "observations": assignment.observations,
        "vehicle": {
            "id_vehicle": incident.vehicle.id_vehicle,
            "plate": incident.vehicle.plate,
            "brand": incident.vehicle.brand,
            "model": incident.vehicle.model,
            "year": incident.vehicle.year,
            "color": incident.vehicle.color,
            "type": incident.vehicle.type,
        },
        "technician": {
            "id_technician": technician.id_technician,
            "name": technician.name,
            "phone": technician.phone,
            "specialty": technician.specialty,
        }
        if technician
        else None,
        "ai_analysis": {
            "classification": ai_analysis.classification,
            "priority_level": ai_analysis.priority_level,
            "structured_summary": ai_analysis.structured_summary,
        }
        if ai_analysis
        else None,
    }


def list_workshop_history(
    db: Session,
    workshop_id: int,
    filters: AssignmentHistoryFilterParams,
) -> list[dict]:
    stmt = _base_history_query(workshop_id)
    stmt = _apply_history_filters(stmt, filters)
    stmt = stmt.order_by(Assignment.assigned_at.desc(), Assignment.id_assignment.desc())

    assignments = list(db.scalars(stmt))
    return [_serialize_history_item(assignment) for assignment in assignments]


def get_workshop_history_detail(db: Session, workshop_id: int, incident_id: int) -> dict:
    stmt = (
        _base_history_query(workshop_id)
        .where(Assignment.id_incident == incident_id)
        .order_by(Assignment.id_assignment.desc())
    )
    assignment = db.scalar(stmt)
    if not assignment:
        raise LookupError("No existe historial de atencion para ese incidente en este taller")

    return _serialize_history_item(assignment)
