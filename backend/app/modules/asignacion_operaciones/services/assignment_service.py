from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Assignment, Incident
from app.modules.asignacion_operaciones.schemas import AssignmentDecisionRequest
from app.modules.gestion_usuarios.services import create_notification


class AssignmentConflictError(Exception):
    pass


def decide_available_request(
    db: Session,
    incident_id: int,
    workshop_id: int,
    data: AssignmentDecisionRequest,
) -> tuple[Assignment, Incident]:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise LookupError("Incidente no encontrado")

    if incident.status != "pendiente":
        raise AssignmentConflictError("El incidente ya no esta disponible para gestion")

    assignment = db.scalar(
        select(Assignment).where(
            Assignment.id_incident == incident_id,
            Assignment.id_workshop == workshop_id,
        )
    )
    now = datetime.now(timezone.utc)

    if assignment is None:
        assignment = Assignment(
            id_incident=incident_id,
            id_workshop=workshop_id,
            status=data.decision,
        )
        db.add(assignment)

    assignment.status = data.decision

    if data.decision == "aceptado":
        assignment.accepted_at = now
        assignment.assigned_at = now
        incident.status = "asignado"
        create_notification(
            db,
            incident.id_client,
            "Solicitud aceptada",
            "Tu solicitud de asistencia fue aceptada por un taller.",
            "assignment",
        )
    else:
        assignment.accepted_at = None
        if assignment.assigned_at is None:
            assignment.assigned_at = now
        # Al rechazar, cancelamos la emergencia para que el flujo termine
        incident.status = "cancelado"
        incident.assigned_workshop_id = None
        create_notification(
            db,
            incident.id_client,
            "Solicitud rechazada",
            "Un taller rechazo tu solicitud de asistencia. La solicitud ha sido cancelada.",
            "assignment",
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar la decision de la solicitud") from exc

    db.refresh(assignment)
    db.refresh(incident)
    return assignment, incident
