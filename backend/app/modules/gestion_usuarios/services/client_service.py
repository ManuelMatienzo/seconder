from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Client, Role, User
from app.modules.gestion_usuarios.schemas import ClientRegisterRequest
from app.shared.security.security import hash_password


CLIENT_ROLE_NAME = "cliente"


def get_or_create_client_role(db: Session) -> Role:
    role = db.scalar(select(Role).where(Role.name == CLIENT_ROLE_NAME))
    if role:
        return role

    role = Role(name=CLIENT_ROLE_NAME, description="Cliente de la plataforma")
    db.add(role)
    db.flush()
    return role


def get_client_by_id(db: Session, client_id: int) -> Client | None:
    return db.get(Client, client_id)


def register_client(db: Session, data: ClientRegisterRequest) -> Client:
    existing_user = db.scalar(select(User).where(User.email == data.email))
    if existing_user:
        raise ValueError("El correo electronico ya esta registrado")

    role = get_or_create_client_role(db)
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

    client = Client(id_user=user.id_user)
    db.add(client)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el cliente con los datos enviados") from exc

    db.refresh(client)
    return client
