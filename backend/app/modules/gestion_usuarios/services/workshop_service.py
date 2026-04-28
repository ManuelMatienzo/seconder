from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Role, User, Workshop
from app.modules.gestion_usuarios.schemas import WorkshopAccountCreateRequest, WorkshopUpsertRequest
from app.shared.security.security import hash_password

WORKSHOP_ROLE_NAME = "taller"


def get_workshop_by_user_id(db: Session, user_id: int) -> Workshop | None:
    return db.get(Workshop, user_id)


def list_workshops(db: Session) -> list[Workshop]:
    stmt = select(Workshop).order_by(Workshop.workshop_name.asc())
    return list(db.scalars(stmt))


def get_or_create_workshop_role(db: Session) -> Role:
    role = db.scalar(select(Role).where(Role.name.in_({WORKSHOP_ROLE_NAME, "workshop"})))
    if role:
        return role

    role = Role(name=WORKSHOP_ROLE_NAME, description="Taller de la plataforma")
    db.add(role)
    db.flush()
    return role


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


def create_workshop_account(db: Session, data: WorkshopAccountCreateRequest) -> Workshop:
    existing_user = db.scalar(select(User).where(User.email == data.email))
    if existing_user:
        raise ValueError("El correo electronico ya esta registrado")

    role = get_or_create_workshop_role(db)
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        status="activo",
        id_role=role.id_role,
    )
    db.add(user)
    db.flush()

    workshop = Workshop(id_user=user.id_user)
    workshop.workshop_name = data.workshop_name
    workshop.address = data.address
    workshop.latitude = data.latitude
    workshop.longitude = data.longitude
    workshop.phone = data.phone
    workshop.specialties = data.specialties
    workshop.is_available = data.is_available
    db.add(workshop)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el taller con los datos enviados") from exc

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


def delete_workshop_by_user_id(db: Session, user_id: int) -> None:
    workshop = get_workshop_by_user_id(db, user_id)
    if workshop is None:
        raise LookupError("Taller no encontrado")

    db.delete(workshop)
    db.commit()
