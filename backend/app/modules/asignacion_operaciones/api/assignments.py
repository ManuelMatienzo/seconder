from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.asignacion_operaciones.schemas import AssignmentDecisionRequest, AssignmentDecisionResponse
from app.modules.asignacion_operaciones.services import AssignmentConflictError, decide_available_request
from app.shared.dependencies.auth import get_current_workshop_user

router = APIRouter(prefix="/operations", tags=["Operations"])

assignment_decision_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "Incidente no encontrado."},
    409: {"description": "El incidente ya no esta disponible para gestion."},
}


@router.patch(
    "/requests/{incident_id}/decision",
    response_model=AssignmentDecisionResponse,
    responses=assignment_decision_responses,
)
def decide_request(
    incident_id: int,
    data: AssignmentDecisionRequest,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> AssignmentDecisionResponse:
    try:
        assignment, incident = decide_available_request(db, incident_id, current_user.id_user, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AssignmentConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AssignmentDecisionResponse(
        id_incident=assignment.id_incident,
        id_workshop=assignment.id_workshop,
        status=assignment.status,
        accepted_at=assignment.accepted_at,
        assigned_at=assignment.assigned_at,
        incident_status=incident.status,
    )
