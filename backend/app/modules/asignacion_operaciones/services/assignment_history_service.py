from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modules.asignacion_operaciones.models.assignment import Assignment
from app.modules.reporte_emergencias.models.incident import Incident
from app.modules.gestion_usuarios.models.client import Client
from app.modules.asignacion_operaciones.schemas.assignment_history import AssignmentHistoryFilterParams
from app.modules.transacciones.models.payment import Payment

DEFAULT_HISTORY_STATUSES = (
    "aceptado",
    "alistando",
    "en_ruta",
    "en_sitio",
    "completado",
    "finalizado",
    "cancelado",
    "rechazado",
)


def _base_history_query(workshop_id: int):
    return (
        select(Assignment)
        .options(
            joinedload(Assignment.incident).joinedload(Incident.vehicle),
            joinedload(Assignment.incident).joinedload(Incident.ai_analysis),
            joinedload(Assignment.incident).joinedload(Incident.client).joinedload(Client.user),
            joinedload(Assignment.incident).joinedload(Incident.photos),
            joinedload(Assignment.incident).joinedload(Incident.audios),
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


def _serialize_history_item(assignment: Assignment, payment: Payment | None) -> dict:
    incident = assignment.incident
    if incident is None or incident.vehicle is None:
        raise LookupError("El assignment no tiene incidente o vehiculo asociado valido")

    ai_analysis = incident.ai_analysis
    technician = assignment.technician

    # Get the most recent photo and audio safely
    latest_photo = None
    if incident.photos:
        try:
            latest_photo = max(incident.photos, key=lambda p: p.created_at if p.created_at else datetime.min)
        except Exception:
            latest_photo = incident.photos[0] if incident.photos else None

    latest_audio = None
    if incident.audios:
        try:
            latest_audio = max(incident.audios, key=lambda a: a.created_at if a.created_at else datetime.min)
        except Exception:
            latest_audio = incident.audios[0] if incident.audios else None

    return {
        "id_assignment": assignment.id_assignment,
        "id_incident": assignment.id_incident,
        "status": assignment.status,
        "assignment_status": assignment.status,
        "incident_status": incident.status,
        "assigned_at": assignment.assigned_at,
        "accepted_at": assignment.accepted_at,
        "completed_at": assignment.completed_at,
        "estimated_time_min": assignment.estimated_time_min,
        "distance_km": assignment.distance_km,
        "service_price": assignment.service_price,
        "observations": assignment.observations,
        "payment_status": payment.payment_status if payment else None,
        "client_name": incident.client.user.name if incident.client and incident.client.user else "Desconocido",
        "vehicle_summary": f"{incident.vehicle.brand} {incident.vehicle.model}" if incident.vehicle else "Vehículo",
        "technician_name": technician.name if technician else "No asignado",
        "incident_description": incident.description_text,
        "photo_url": latest_photo.file_url if latest_photo else None,
        "audio_url": latest_audio.file_url if latest_audio else None,
        "client": {
            "id_client": incident.client.user.id_user,
            "name": incident.client.user.name,
            "phone": incident.client.user.phone,
        }
        if incident.client and incident.client.user
        else None,
        "vehicle": {
            "id_vehicle": incident.vehicle.id_vehicle,
            "license_plate": incident.vehicle.plate,
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
            "audio_transcription": getattr(ai_analysis, 'audio_transcription', None),
            "classification": getattr(ai_analysis, 'classification', None),
            "priority_level": getattr(ai_analysis, 'priority_level', None),
            "structured_summary": getattr(ai_analysis, 'structured_summary', None),
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

    assignments = list(db.scalars(stmt).unique())
    payments_by_assignment: dict[int, Payment] = {}
    if assignments:
        assignment_ids = [assignment.id_assignment for assignment in assignments]
        payments = list(
            db.scalars(select(Payment).where(Payment.id_assignment.in_(assignment_ids)))
        )
        payments_by_assignment = {payment.id_assignment: payment for payment in payments}

    serialized_items = []
    for assignment in assignments:
        try:
            serialized_items.append(
                _serialize_history_item(assignment, payments_by_assignment.get(assignment.id_assignment))
            )
        except (LookupError, AttributeError) as exc:
            # Skip invalid assignments instead of crashing the entire list
            print(f"Skipping assignment {assignment.id_assignment} due to error: {exc}")
            continue
            
    return serialized_items


def get_workshop_history_detail(db: Session, workshop_id: int, incident_id: int) -> dict:
    stmt = (
        _base_history_query(workshop_id)
        .where(Assignment.id_incident == incident_id)
        .order_by(Assignment.id_assignment.desc())
    )
    assignment = db.scalars(stmt).unique().first()
    if not assignment:
        raise LookupError("No existe historial de atencion para ese incidente en este taller")
    payment = db.scalar(select(Payment).where(Payment.id_assignment == assignment.id_assignment))
    return _serialize_history_item(assignment, payment)
