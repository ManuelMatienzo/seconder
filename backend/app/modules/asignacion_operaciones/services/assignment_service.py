from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from anyio import from_thread

from app.models import Assignment, Incident, Workshop
from app.modules.asignacion_operaciones.services.assignment_engine_service import (
    estimate_time_minutes,
    haversine_distance_km,
)
from app.modules.asignacion_operaciones.schemas import AssignmentDecisionRequest
from app.modules.gestion_usuarios.services import create_notification
from app.shared.realtime import notification_manager


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
        workshop = db.get(Workshop, workshop_id)
        if workshop and workshop.latitude is not None and workshop.longitude is not None:
            distance_km = haversine_distance_km(
                float(incident.latitude),
                float(incident.longitude),
                float(workshop.latitude),
                float(workshop.longitude),
            )
            assignment.distance_km = Decimal(str(distance_km)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            assignment.estimated_time_min = estimate_time_minutes(distance_km)
        create_notification(
            db,
            incident.id_client,
            "Solicitud aceptada",
            "Tu solicitud de asistencia fue aceptada por un taller.",
            "assignment",
        )
        try:
            from_thread.run(
                notification_manager.send_to_user,
                incident.id_client,
                {
                    "type": "request_accepted",
                    "incident_id": incident.id_incident,
                    "workshop_name": workshop.workshop_name if workshop else None,
                },
            )
        except Exception:
            pass
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
