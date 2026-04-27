from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Technician
from app.modules.gestion_usuarios.schemas import (
    TechnicianAvailabilityUpdateRequest,
    TechnicianCreateRequest,
    TechnicianUpdateRequest,
)


def create_technician(db: Session, workshop_id: int, data: TechnicianCreateRequest) -> Technician:
    technician = Technician(
        id_workshop=workshop_id,
        name=data.name,
        phone=data.phone,
        specialty=data.specialty,
        is_available=data.is_available,
    )
    db.add(technician)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el tecnico con los datos enviados") from exc

    db.refresh(technician)
    return technician


def list_workshop_technicians(db: Session, workshop_id: int) -> list[Technician]:
    return list(
        db.scalars(
            select(Technician)
            .where(Technician.id_workshop == workshop_id)
            .order_by(Technician.created_at.desc(), Technician.id_technician.desc())
        )
    )


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


def update_technician(
    db: Session,
    workshop_id: int,
    technician_id: int,
    data: TechnicianUpdateRequest,
) -> Technician:
    technician = get_workshop_technician_or_404(db, workshop_id, technician_id)
    technician.name = data.name
    technician.phone = data.phone
    technician.specialty = data.specialty
    technician.is_available = data.is_available

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo actualizar el tecnico") from exc

    db.refresh(technician)
    return technician


def update_technician_availability(
    db: Session,
    workshop_id: int,
    technician_id: int,
    data: TechnicianAvailabilityUpdateRequest,
) -> Technician:
    technician = get_workshop_technician_or_404(db, workshop_id, technician_id)
    technician.is_available = data.is_available

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo actualizar la disponibilidad del tecnico") from exc

    db.refresh(technician)
    return technician
