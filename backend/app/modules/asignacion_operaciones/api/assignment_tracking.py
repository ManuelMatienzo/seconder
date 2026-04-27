from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.asignacion_operaciones.schemas import AssignmentTrackingResponse, AssignmentTrackingUpdateRequest
from app.modules.asignacion_operaciones.services import (
    AssignmentTrackingConflictError,
    get_assignment_tracking,
    update_assignment_tracking,
)
from app.shared.dependencies.auth import get_current_workshop_user

router = APIRouter(prefix="/operations", tags=["Operations"])

assignment_tracking_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "Incidente o assignment no encontrado para el taller autenticado."},
    409: {"description": "La transicion de estado no es valida para el assignment actual."},
}


@router.get(
    "/assignments/{incident_id}/tracking",
    response_model=AssignmentTrackingResponse,
    responses=assignment_tracking_responses,
)
def get_tracking(
    incident_id: int,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> AssignmentTrackingResponse:
    try:
        return AssignmentTrackingResponse.model_validate(
            get_assignment_tracking(db, incident_id, current_user.id_user)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/assignments/{incident_id}/tracking",
    response_model=AssignmentTrackingResponse,
    responses=assignment_tracking_responses,
)
def patch_tracking(
    incident_id: int,
    data: AssignmentTrackingUpdateRequest,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> AssignmentTrackingResponse:
    try:
        assignment, incident = update_assignment_tracking(db, incident_id, current_user.id_user, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AssignmentTrackingConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AssignmentTrackingResponse.model_validate(
        {
            "id_assignment": assignment.id_assignment,
            "id_incident": assignment.id_incident,
            "id_workshop": assignment.id_workshop,
            "id_technician": assignment.id_technician,
            "status": assignment.status,
            "estimated_time_min": assignment.estimated_time_min,
            "distance_km": assignment.distance_km,
            "service_price": assignment.service_price,
            "observations": assignment.observations,
            "assigned_at": assignment.assigned_at,
            "accepted_at": assignment.accepted_at,
            "completed_at": assignment.completed_at,
            "incident_status": incident.status,
            "workshop": {
                "id_workshop": assignment.id_workshop,
                "workshop_name": assignment.workshop.workshop_name if assignment.workshop else f"Taller {assignment.id_workshop}",
            },
            "technician": {
                "id_technician": assignment.technician.id_technician,
                "name": assignment.technician.name,
                "phone": assignment.technician.phone,
                "specialty": assignment.technician.specialty,
                "is_available": assignment.technician.is_available,
            }
            if assignment.technician
            else None,
        }
    )
