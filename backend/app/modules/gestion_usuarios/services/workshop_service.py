from sqlalchemy.orm import Session

from app.models import Workshop
from app.modules.gestion_usuarios.schemas import WorkshopUpsertRequest


def get_workshop_by_user_id(db: Session, user_id: int) -> Workshop | None:
    return db.get(Workshop, user_id)


def upsert_workshop_for_user(db: Session, user_id: int, data: WorkshopUpsertRequest) -> Workshop:
    workshop = get_workshop_by_user_id(db, user_id)
    if workshop is None:
        workshop = Workshop(id_user=user_id)
        db.add(workshop)

    workshop.workshop_name = data.workshop_name
    workshop.address = data.address
    workshop.latitude = data.latitude
    workshop.longitude = data.longitude
    workshop.phone = data.phone
    workshop.specialties = data.specialties
    workshop.is_available = data.is_available

    db.commit()
    db.refresh(workshop)
    return workshop


def update_workshop_for_user(db: Session, user_id: int, data: WorkshopUpsertRequest) -> Workshop:
    workshop = get_workshop_by_user_id(db, user_id)
    if workshop is None:
        raise LookupError("Taller no encontrado")

    workshop.workshop_name = data.workshop_name
    workshop.address = data.address
    workshop.latitude = data.latitude
    workshop.longitude = data.longitude
    workshop.phone = data.phone
    workshop.specialties = data.specialties
    workshop.is_available = data.is_available

    db.commit()
    db.refresh(workshop)
    return workshop
