from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.asignacion_operaciones.schemas import ClientIncidentStatusResponse
from app.modules.asignacion_operaciones.services import get_client_incident_status
from app.shared.dependencies.auth import get_current_client, get_incident_owned_by_current_client

router = APIRouter(prefix="/client/incidents", tags=["Client Incidents"])

client_status_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no pertenece a clients."},
    404: {"description": "Incidente no encontrado para el cliente autenticado."},
}


@router.get(
    "/{incident_id}/status",
    response_model=ClientIncidentStatusResponse,
    responses=client_status_responses,
)
def get_client_status(
    incident_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> ClientIncidentStatusResponse:
    incident = get_incident_owned_by_current_client(db, current_client, incident_id)
    return ClientIncidentStatusResponse.model_validate(get_client_incident_status(db, incident))
