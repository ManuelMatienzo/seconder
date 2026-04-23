from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client, Incident, User, Vehicle
from app.shared.security.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise auth_error

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub", ""))
    except (TypeError, ValueError):
        raise auth_error

    user = db.get(User, user_id)
    if not user or user.status != "activo":
        raise auth_error

    return user


def get_current_client(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Client:
    client = db.get(Client, current_user.id_user)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario autenticado no pertenece a clients",
        )

    return client


def ensure_client_ownership(current_client: Client, client_id: int) -> None:
    if current_client.id_user != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a los recursos de otro cliente",
        )


def get_vehicle_owned_by_current_client(db: Session, current_client: Client, vehicle_id: int) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehiculo no encontrado")

    if vehicle.id_client != current_client.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre ese vehiculo",
        )

    return vehicle


def get_incident_owned_by_current_client(db: Session, current_client: Client, incident_id: int) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")

    if incident.id_client != current_client.id_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre ese incidente",
        )

    return incident
