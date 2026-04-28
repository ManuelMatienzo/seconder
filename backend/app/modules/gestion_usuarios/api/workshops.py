from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Workshop
from app.modules.gestion_usuarios.schemas import (
    WorkshopAccountCreateRequest,
    WorkshopAdminUpsertRequest,
    WorkshopResponse,
    WorkshopUpsertRequest,
)
from app.modules.gestion_usuarios.services import (
    create_workshop_account,
    delete_workshop_by_user_id,
    list_workshops,
    update_workshop_for_user,
    upsert_workshop_for_user,
)
from app.shared.dependencies.auth import (
    get_current_admin_user,
    get_current_workshop,
    get_current_workshop_user,
)

router = APIRouter(prefix="/workshops", tags=["Workshops"])

workshop_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "Taller no encontrado."},
}

admin_workshop_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de administrador."},
    404: {"description": "Taller no encontrado."},
}


@router.get("", response_model=list[WorkshopResponse], responses=admin_workshop_responses)
def list_all_workshops(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[WorkshopResponse]:
    _ = current_user
    return list_workshops(db)


@router.post(
    "",
    response_model=WorkshopResponse,
    status_code=status.HTTP_201_CREATED,
    responses=admin_workshop_responses,
)
def create_workshop(
    data: WorkshopAdminUpsertRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> WorkshopResponse:
    _ = current_user
    workshop = upsert_workshop_for_user(db, data.id_user, data)
    return workshop


@router.post(
    "/register",
    response_model=WorkshopResponse,
    status_code=status.HTTP_201_CREATED,
    responses=admin_workshop_responses,
)
def register_workshop_account(
    data: WorkshopAccountCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> WorkshopResponse:
    _ = current_user
    try:
        return create_workshop_account(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put(
    "/{user_id}",
    response_model=WorkshopResponse,
    responses=admin_workshop_responses,
)
def update_workshop(
    user_id: int,
    data: WorkshopUpsertRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> WorkshopResponse:
    _ = current_user
    try:
        return update_workshop_for_user(db, user_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=admin_workshop_responses,
)
def delete_workshop(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    _ = current_user
    try:
        delete_workshop_by_user_id(db, user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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
