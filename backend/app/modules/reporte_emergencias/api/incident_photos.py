from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.reporte_emergencias.schemas import IncidentPhotoCreateRequest, IncidentPhotoResponse
from app.modules.reporte_emergencias.services import create_incident_photo
from app.shared.dependencies.auth import get_current_client, get_incident_owned_by_current_client

router = APIRouter(prefix="/incident-photos", tags=["Incident Photos"])

protected_incident_photo_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "No tienes permisos para adjuntar evidencia a ese incidente."},
    404: {"description": "Incidente no encontrado."},
}


@router.post(
    "",
    response_model=IncidentPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    responses=protected_incident_photo_responses,
)
def upload_incident_photo(
    data: IncidentPhotoCreateRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> IncidentPhotoResponse:
    if data.id_incident is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_incident es requerido")

    get_incident_owned_by_current_client(db, current_client, data.id_incident)

    try:
        return create_incident_photo(db, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
