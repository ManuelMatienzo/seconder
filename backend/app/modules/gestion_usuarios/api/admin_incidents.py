from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.gestion_usuarios.schemas import AdminIncidentResponse
from app.modules.gestion_usuarios.services import list_admin_incidents
from app.shared.dependencies.admin import get_current_admin

router = APIRouter(prefix="/admin/incidents", tags=["Admin"])

admin_incident_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de administrador."},
}


@router.get("", response_model=list[AdminIncidentResponse], responses=admin_incident_responses)
def get_admin_incidents(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminIncidentResponse]:
    _ = current_user
    return [AdminIncidentResponse.model_validate(item) for item in list_admin_incidents(db)]
