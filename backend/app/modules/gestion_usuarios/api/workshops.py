from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Workshop
from app.modules.gestion_usuarios.schemas import (
    WorkshopResponse,
    WorkshopTestRegisterRequest,
    WorkshopTestRegisterResponse,
    WorkshopUpsertRequest,
)
from app.modules.gestion_usuarios.services import (
    register_test_workshop_user,
    update_workshop_for_user,
    upsert_workshop_for_user,
)
from app.shared.dependencies.auth import get_current_workshop, get_current_workshop_user

router = APIRouter(prefix="/workshops", tags=["Workshops"])

workshop_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "Taller no encontrado."},
}


@router.post(
    "/test-register",
    response_model=WorkshopTestRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_test_workshop(
    data: WorkshopTestRegisterRequest,
    db: Session = Depends(get_db),
) -> WorkshopTestRegisterResponse:
    try:
        user = register_test_workshop_user(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return WorkshopTestRegisterResponse(
        message="Usuario taller de prueba registrado correctamente",
        id_user=user.id_user,
        email=user.email,
        id_role=user.id_role,
    )


@router.post(
    "/me",
    response_model=WorkshopResponse,
    status_code=status.HTTP_201_CREATED,
    responses=workshop_responses,
)
def register_or_complete_workshop(
    data: WorkshopUpsertRequest,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> WorkshopResponse:
    workshop = upsert_workshop_for_user(db, current_user.id_user, data)
    return workshop


@router.get("/me", response_model=WorkshopResponse, responses=workshop_responses)
def get_my_workshop(current_workshop: Workshop = Depends(get_current_workshop)) -> WorkshopResponse:
    return current_workshop


@router.put("/me", response_model=WorkshopResponse, responses=workshop_responses)
def update_my_workshop(
    data: WorkshopUpsertRequest,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> WorkshopResponse:
    try:
        return update_workshop_for_user(db, current_user.id_user, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
