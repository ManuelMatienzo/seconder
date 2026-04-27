from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.gestion_usuarios.schemas import (
    AdminUserDetailResponse,
    AdminUserListItemResponse,
    AdminUserStatusUpdateRequest,
    AdminUserStatusUpdateResponse,
)
from app.modules.gestion_usuarios.services import (
    get_admin_user_detail,
    list_admin_users,
    update_admin_user_status,
)
from app.shared.dependencies.admin import get_current_admin

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

admin_user_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de administrador."},
    404: {"description": "Usuario no encontrado."},
}


@router.get("", response_model=list[AdminUserListItemResponse], responses=admin_user_responses)
def get_admin_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserListItemResponse]:
    _ = current_user
    return [AdminUserListItemResponse.model_validate(item) for item in list_admin_users(db)]


@router.get("/{user_id}", response_model=AdminUserDetailResponse, responses=admin_user_responses)
def get_admin_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserDetailResponse:
    _ = current_user
    try:
        return AdminUserDetailResponse.model_validate(get_admin_user_detail(db, user_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/{user_id}/status",
    response_model=AdminUserStatusUpdateResponse,
    responses=admin_user_responses,
)
def patch_admin_user_status(
    user_id: int,
    data: AdminUserStatusUpdateRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserStatusUpdateResponse:
    _ = current_user
    try:
        return AdminUserStatusUpdateResponse.model_validate(update_admin_user_status(db, user_id, data.status))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
