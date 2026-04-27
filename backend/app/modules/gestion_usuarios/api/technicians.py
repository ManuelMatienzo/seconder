from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Workshop
from app.modules.gestion_usuarios.schemas import (
    TechnicianAvailabilityUpdateRequest,
    TechnicianCreateRequest,
    TechnicianResponse,
    TechnicianUpdateRequest,
)
from app.modules.gestion_usuarios.services import (
    create_technician,
    get_workshop_technician_or_404,
    list_workshop_technicians,
    update_technician,
    update_technician_availability,
)
from app.shared.dependencies.auth import get_current_workshop

router = APIRouter(prefix="/technicians", tags=["Technicians"])

technician_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "Tecnico no encontrado."},
}


@router.post(
    "",
    response_model=TechnicianResponse,
    status_code=status.HTTP_201_CREATED,
    responses=technician_responses,
)
def register_technician(
    data: TechnicianCreateRequest,
    current_workshop: Workshop = Depends(get_current_workshop),
    db: Session = Depends(get_db),
) -> TechnicianResponse:
    try:
        return create_technician(db, current_workshop.id_user, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[TechnicianResponse], responses=technician_responses)
def get_my_technicians(
    current_workshop: Workshop = Depends(get_current_workshop),
    db: Session = Depends(get_db),
) -> list[TechnicianResponse]:
    return list_workshop_technicians(db, current_workshop.id_user)


@router.get(
    "/{technician_id}",
    response_model=TechnicianResponse,
    responses=technician_responses,
)
def get_my_technician(
    technician_id: int,
    current_workshop: Workshop = Depends(get_current_workshop),
    db: Session = Depends(get_db),
) -> TechnicianResponse:
    try:
        return get_workshop_technician_or_404(db, current_workshop.id_user, technician_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/{technician_id}",
    response_model=TechnicianResponse,
    responses=technician_responses,
)
def put_my_technician(
    technician_id: int,
    data: TechnicianUpdateRequest,
    current_workshop: Workshop = Depends(get_current_workshop),
    db: Session = Depends(get_db),
) -> TechnicianResponse:
    try:
        return update_technician(db, current_workshop.id_user, technician_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch(
    "/{technician_id}/availability",
    response_model=TechnicianResponse,
    responses=technician_responses,
)
def patch_my_technician_availability(
    technician_id: int,
    data: TechnicianAvailabilityUpdateRequest,
    current_workshop: Workshop = Depends(get_current_workshop),
    db: Session = Depends(get_db),
) -> TechnicianResponse:
    try:
        return update_technician_availability(db, current_workshop.id_user, technician_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
