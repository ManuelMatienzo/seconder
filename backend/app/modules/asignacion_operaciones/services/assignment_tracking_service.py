from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Assignment, Incident, Technician
from app.modules.asignacion_operaciones.schemas import AssignmentTrackingUpdateRequest
from app.modules.gestion_usuarios.services import create_notification

TERMINAL_TRACKING_STATUSES = {"rechazado", "completado", "cancelado"}
VALID_TRANSITIONS: dict[str, set[str]] = {
    "aceptado": {"en_camino", "cancelado"},
    "en_camino": {"completado", "cancelado"},
}


class AssignmentTrackingConflictError(Exception):
    pass


def get_workshop_assignment_or_404(db: Session, incident_id: int, workshop_id: int) -> Assignment:
    assignment = db.scalar(
        select(Assignment)
        .options(joinedload(Assignment.technician), joinedload(Assignment.workshop))
        .where(
            Assignment.id_incident == incident_id,
            Assignment.id_workshop == workshop_id,
        )
        .order_by(Assignment.id_assignment.desc())
    )
    if not assignment:
        raise LookupError("Assignment no encontrado para este taller e incidente")

    return assignment


def get_tracking_payload(assignment: Assignment, incident: Incident) -> dict:
    workshop_name = assignment.workshop.workshop_name if assignment.workshop else f"Taller {assignment.id_workshop}"
    technician_payload = None
    if assignment.technician:
        technician_payload = {
            "id_technician": assignment.technician.id_technician,
            "name": assignment.technician.name,
            "phone": assignment.technician.phone,
            "specialty": assignment.technician.specialty,
            "is_available": assignment.technician.is_available,
        }

    return {
        "id_assignment": assignment.id_assignment,
        "id_incident": assignment.id_incident,
        "id_workshop": assignment.id_workshop,
        "id_technician": assignment.id_technician,
        "status": assignment.status,
        "estimated_time_min": assignment.estimated_time_min,
        "distance_km": assignment.distance_km,
        "service_price": assignment.service_price,
        "observations": assignment.observations,
        "assigned_at": assignment.assigned_at,
        "accepted_at": assignment.accepted_at,
        "completed_at": assignment.completed_at,
        "incident_status": incident.status,
        "workshop": {
            "id_workshop": assignment.id_workshop,
            "workshop_name": workshop_name,
        },
        "technician": technician_payload,
    }


def get_assignment_tracking(db: Session, incident_id: int, workshop_id: int) -> dict:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise LookupError("Incidente no encontrado")

    assignment = get_workshop_assignment_or_404(db, incident_id, workshop_id)
    return get_tracking_payload(assignment, incident)


def get_workshop_technician_or_404(db: Session, workshop_id: int, technician_id: int) -> Technician:
    technician = db.scalar(
        select(Technician).where(
            Technician.id_technician == technician_id,
            Technician.id_workshop == workshop_id,
        )
    )
    if not technician:
        raise LookupError("Tecnico no encontrado")

    return technician


def ensure_valid_transition(current_status: str, new_status: str) -> None:
    if current_status == new_status:
        return

    if current_status in TERMINAL_TRACKING_STATUSES:
        raise AssignmentTrackingConflictError("El assignment ya esta en un estado terminal y no puede avanzar")

    allowed_statuses = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_statuses:
        raise AssignmentTrackingConflictError(
            f"Transicion invalida de estado: {current_status} -> {new_status}"
        )


def reflect_incident_status_from_assignment(assignment_status: str, incident: Incident) -> None:
    if assignment_status == "aceptado":
        incident.status = "asignado"
    elif assignment_status == "en_camino":
        incident.status = "en_camino"
    elif assignment_status == "completado":
        incident.status = "atendido"
    elif assignment_status == "cancelado":
        incident.status = "cancelado"


def update_assignment_tracking(
    db: Session,
    incident_id: int,
    workshop_id: int,
    data: AssignmentTrackingUpdateRequest,
) -> tuple[Assignment, Incident]:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise LookupError("Incidente no encontrado")

    assignment = get_workshop_assignment_or_404(db, incident_id, workshop_id)

    previous_technician = assignment.technician
    next_technician = previous_technician
    now = datetime.now(timezone.utc)

    if data.id_technician is not None:
        next_technician = get_workshop_technician_or_404(db, workshop_id, data.id_technician)
        if previous_technician and previous_technician.id_technician != next_technician.id_technician:
            previous_technician.is_available = True
        assignment.id_technician = next_technician.id_technician
        next_technician.is_available = False

    if data.status is not None:
        ensure_valid_transition(assignment.status, data.status)
        assignment.status = data.status

        if data.status == "en_camino" and assignment.id_technician is None:
            raise AssignmentTrackingConflictError("Debes asignar un tecnico antes de marcar el servicio como en_camino")

        if data.status == "completado":
            assignment.completed_at = now
            if next_technician:
                next_technician.is_available = True
        elif data.status == "cancelado":
            if next_technician:
                next_technician.is_available = True
        elif data.status == "aceptado" and assignment.accepted_at is None:
            assignment.accepted_at = now

        reflect_incident_status_from_assignment(assignment.status, incident)

        if data.status == "en_camino":
            create_notification(
                db,
                incident.id_client,
                "Servicio en camino",
                "El tecnico ya esta en ruta hacia tu ubicacion.",
                "tracking",
            )
        elif data.status == "completado":
            create_notification(
                db,
                incident.id_client,
                "Servicio completado",
                "La atencion de tu incidente fue completada.",
                "tracking",
            )

    if data.estimated_time_min is not None:
        assignment.estimated_time_min = data.estimated_time_min
    if data.distance_km is not None:
        assignment.distance_km = Decimal(data.distance_km)
    if data.service_price is not None:
        assignment.service_price = Decimal(data.service_price)
    if data.observations is not None:
        assignment.observations = data.observations

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo actualizar la trazabilidad del assignment") from exc

    db.refresh(assignment)
    db.refresh(incident)
    return assignment, incident
