from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Role, User, Workshop
from app.modules.gestion_usuarios.schemas import WorkshopTestRegisterRequest, WorkshopUpsertRequest
from app.shared.security.security import hash_password


WORKSHOP_ROLE_ID = 2


def get_workshop_by_user_id(db: Session, user_id: int) -> Workshop | None:
    return db.get(Workshop, user_id)


def register_test_workshop_user(db: Session, data: WorkshopTestRegisterRequest) -> User:
    existing_user = db.scalar(select(User).where(User.email == data.email))
    if existing_user:
        raise ValueError("El correo electronico ya esta registrado")

    role = db.get(Role, WORKSHOP_ROLE_ID)
    if role is None:
        raise ValueError("No existe el role workshop con id_role=2")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        status="activo",
        id_role=WORKSHOP_ROLE_ID,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el usuario taller de prueba") from exc

    db.refresh(user)
    return user


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
