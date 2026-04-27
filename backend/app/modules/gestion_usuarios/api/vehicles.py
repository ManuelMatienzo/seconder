from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.gestion_usuarios.schemas import VehicleCreateRequest, VehicleResponse
from app.modules.gestion_usuarios.services import create_vehicle, list_client_vehicles
from app.shared.dependencies.auth import ensure_client_ownership, get_current_client

router = APIRouter(tags=["Vehicles"])

protected_vehicle_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "Acceso denegado para el cliente autenticado."},
    404: {"description": "Recurso no encontrado."},
}


@router.post(
    "/vehicles",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    responses=protected_vehicle_responses,
)
def register_vehicle(
    data: VehicleCreateRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> VehicleResponse:
    try:
        return create_vehicle(db, current_client.id_user, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/clients/{client_id}/vehicles",
    response_model=list[VehicleResponse],
    responses=protected_vehicle_responses,
)
def get_client_vehicles(
    client_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> list[VehicleResponse]:
    ensure_client_ownership(current_client, client_id)

    try:
        return list_client_vehicles(db, client_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
