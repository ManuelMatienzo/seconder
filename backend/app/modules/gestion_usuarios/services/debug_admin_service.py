from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Role, User
from app.modules.gestion_usuarios.schemas import DebugAdminCreateRequest
from app.shared.security.security import hash_password


ADMIN_ROLE_NAME = "admin"


def create_debug_admin(db: Session, data: DebugAdminCreateRequest) -> User:
    existing_user = db.scalar(select(User).where(User.email == data.email))
    if existing_user:
        raise FileExistsError("El correo electronico ya esta registrado")

    admin_role = db.scalar(select(Role).where(Role.name == ADMIN_ROLE_NAME))
    if not admin_role:
        raise LookupError("El rol admin no existe en la base de datos")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=None,
        status="activo",
        id_role=admin_role.id_role,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo crear el usuario administrador de prueba") from exc

    db.refresh(user)
    return user
