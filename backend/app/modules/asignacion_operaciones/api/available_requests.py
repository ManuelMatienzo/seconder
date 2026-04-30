from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.gestion_usuarios.models.user import User
from app.modules.asignacion_operaciones.schemas.available_request import AvailableRequestResponse
from app.modules.asignacion_operaciones.services.available_request_service import list_available_requests
from app.shared.dependencies.auth import get_current_workshop_user

router = APIRouter(prefix="/operations", tags=["Operations"])

available_request_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
}


@router.get(
    "/available-requests",
    response_model=list[AvailableRequestResponse],
    responses=available_request_responses,
)
def get_available_requests(
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> list[AvailableRequestResponse]:
    return list_available_requests(db, workshop_id=current_user.id_user)
