from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.reporte_emergencias.schemas import IncidentCreateRequest, IncidentResponse
from app.modules.reporte_emergencias.services import create_incident, get_incident_by_id
from app.shared.dependencies.auth import get_current_client, get_incident_owned_by_current_client

router = APIRouter(prefix="/incidents", tags=["Incidents"])

protected_incident_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "Acceso denegado para el cliente autenticado."},
    404: {"description": "Incidente o recurso asociado no encontrado."},
}


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=protected_incident_responses,
)
def report_incident(
    data: IncidentCreateRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    try:
        return create_incident(db, current_client.id_user, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    responses=protected_incident_responses,
)
def get_incident(
    incident_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    get_incident_owned_by_current_client(db, current_client, incident_id)
    incident = get_incident_by_id(db, incident_id)
    return incident
