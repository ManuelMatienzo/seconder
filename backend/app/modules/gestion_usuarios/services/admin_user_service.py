from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import User


ACTIVE_STATUS = "activo"
BLOCKED_STATUS = "bloqueado"


def _is_active(user: User) -> bool:
    return user.status == ACTIVE_STATUS


def _role_name(user: User) -> str | None:
    return user.role.name if user.role else None


def _user_type(user: User) -> str | None:
    role_name = (user.role.name.lower() if user.role and user.role.name else "")
    if user.client is not None or role_name in {"client", "cliente"}:
        return "client"
    if user.workshop is not None or role_name in {"workshop", "taller"}:
        return "workshop"
    if role_name in {"admin", "administrador"}:
        return "admin"
    return role_name or None


def _serialize_user_list_item(user: User) -> dict:
    return {
        "id_user": user.id_user,
        "email": user.email,
        "role": _role_name(user),
        "is_active": _is_active(user),
        "status": user.status,
    }


def _serialize_user_detail(user: User) -> dict:
    return {
        "id_user": user.id_user,
        "email": user.email,
        "role": _role_name(user),
        "is_active": _is_active(user),
        "status": user.status,
        "type": _user_type(user),
        "client": {
            "id_user": user.client.id_user,
        }
        if user.client
        else None,
        "workshop": {
            "id_user": user.workshop.id_user,
            "workshop_name": user.workshop.workshop_name,
            "address": user.workshop.address,
            "latitude": user.workshop.latitude,
            "longitude": user.workshop.longitude,
            "phone": user.workshop.phone,
            "specialties": user.workshop.specialties,
            "is_available": user.workshop.is_available,
            "rating": user.workshop.rating,
        }
        if user.workshop
        else None,
    }


def list_admin_users(db: Session) -> list[dict]:
    stmt = select(User).options(joinedload(User.role)).order_by(User.id_user.asc())
    users = list(db.scalars(stmt))
    return [_serialize_user_list_item(user) for user in users]


def get_admin_user_detail(db: Session, user_id: int) -> dict:
    stmt = (
        select(User)
        .options(
            joinedload(User.role),
            joinedload(User.client),
            joinedload(User.workshop),
        )
        .where(User.id_user == user_id)
    )
    user = db.scalar(stmt)
    if not user:
        raise LookupError("Usuario no encontrado")

    return _serialize_user_detail(user)


def update_admin_user_status(db: Session, user_id: int, status_value: str) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise LookupError("Usuario no encontrado")

    user.status = status_value
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id_user": user.id_user,
        "status": user.status,
        "is_active": _is_active(user),
    }
