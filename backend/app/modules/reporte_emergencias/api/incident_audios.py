from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.reporte_emergencias.schemas import IncidentAudioCreateRequest, IncidentAudioResponse
from app.modules.reporte_emergencias.services import create_incident_audio
from app.shared.dependencies.auth import get_current_client, get_incident_owned_by_current_client

router = APIRouter(prefix="/incident-audios", tags=["Incident Audios"])

protected_incident_audio_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "No tienes permisos para adjuntar evidencia a ese incidente."},
    404: {"description": "Incidente no encontrado."},
}


@router.post(
    "",
    response_model=IncidentAudioResponse,
    status_code=status.HTTP_201_CREATED,
    responses=protected_incident_audio_responses,
)
def upload_incident_audio(
    data: IncidentAudioCreateRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> IncidentAudioResponse:
    if data.id_incident is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="id_incident es requerido")

    get_incident_owned_by_current_client(db, current_client, data.id_incident)

    try:
        return create_incident_audio(db, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
