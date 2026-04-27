from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.asignacion_operaciones.schemas import AssignmentHistoryFilterParams, AssignmentHistoryItemResponse
from app.modules.asignacion_operaciones.services import get_workshop_history_detail, list_workshop_history
from app.shared.dependencies.auth import get_current_workshop_user

router = APIRouter(prefix="/operations", tags=["Operations"])

assignment_history_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de taller."},
    404: {"description": "No existe historial para ese incidente en el taller autenticado."},
}


@router.get(
    "/history",
    response_model=list[AssignmentHistoryItemResponse],
    responses=assignment_history_responses,
)
def get_history(
    status: str | None = None,
    id_technician: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> list[AssignmentHistoryItemResponse]:
    filters = AssignmentHistoryFilterParams(
        status=status,
        id_technician=id_technician,
        date_from=date_from,
        date_to=date_to,
    )
    return [AssignmentHistoryItemResponse.model_validate(item) for item in list_workshop_history(db, current_user.id_user, filters)]


@router.get(
    "/history/{incident_id}",
    response_model=AssignmentHistoryItemResponse,
    responses=assignment_history_responses,
)
def get_history_detail(
    incident_id: int,
    current_user: User = Depends(get_current_workshop_user),
    db: Session = Depends(get_db),
) -> AssignmentHistoryItemResponse:
    try:
        return AssignmentHistoryItemResponse.model_validate(
            get_workshop_history_detail(db, current_user.id_user, incident_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
