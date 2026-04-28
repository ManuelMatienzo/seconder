from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.gestion_usuarios.schemas import (
    ClientAdminResponse,
    ClientRegisterRequest,
    ClientRegisterResponse,
    ClientUpdateRequest,
)
from app.modules.gestion_usuarios.services import (
    delete_client,
    list_clients,
    register_client,
    update_client,
)
from app.shared.dependencies.auth import get_current_admin_user

router = APIRouter(prefix="/clients", tags=["Clients"])

admin_client_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de administrador."},
    404: {"description": "Cliente no encontrado."},
}


@router.get("", response_model=list[ClientAdminResponse], responses=admin_client_responses)
def list_all_clients(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[ClientAdminResponse]:
    _ = current_user
    clients = list_clients(db)
    return [
        ClientAdminResponse(
            id_user=c.id_user,
            name=c.user.name,
            email=c.user.email,
            phone=c.user.phone,
            status=c.user.status,
            created_at=c.user.created_at,
        )
        for c in clients
        if c.user
    ]


@router.post(
    "/register",
    response_model=ClientRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client_account(
    data: ClientRegisterRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> ClientRegisterResponse:
    _ = current_user
    try:
        client = register_client(db, data)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a la base de datos. Verifica las credenciales.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ClientRegisterResponse(message="Cliente registrado correctamente", client=client)


@router.put(
    "/{client_id}",
    response_model=ClientAdminResponse,
    responses=admin_client_responses,
)
def update_client_data(
    client_id: int,
    data: ClientUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> ClientAdminResponse:
    _ = current_user
    try:
        c = update_client(db, client_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ClientAdminResponse(
        id_user=c.id_user,
        name=c.user.name,
        email=c.user.email,
        phone=c.user.phone,
        status=c.user.status,
        created_at=c.user.created_at,
    )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=admin_client_responses,
)
def delete_client_account(
    client_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    _ = current_user
    try:
        delete_client(db, client_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
