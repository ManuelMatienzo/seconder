from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Client, Role, User
from app.modules.gestion_usuarios.schemas import ClientRegisterRequest, ClientUpdateRequest
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


def list_clients(db: Session) -> list[Client]:
    stmt = (
        select(Client)
        .options(joinedload(Client.user))
        .join(Client.user)
        .order_by(User.name.asc())
    )
    return list(db.scalars(stmt))


def update_client(db: Session, client_id: int, data: ClientUpdateRequest) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise LookupError("Cliente no encontrado")

    user = client.user
    if user is None:
        raise LookupError("Usuario del cliente no encontrado")

    duplicate = db.scalar(
        select(User).where(User.email == data.email, User.id_user != client_id)
    )
    if duplicate:
        raise ValueError("El correo electronico ya esta en uso por otro usuario")

    user.name = data.name
    user.email = data.email
    user.phone = data.phone

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int) -> None:
    client = db.get(Client, client_id)
    if client is None:
        raise LookupError("Cliente no encontrado")

    user = client.user
    db.delete(client)
    db.flush()
    if user:
        db.delete(user)
    db.commit()


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
