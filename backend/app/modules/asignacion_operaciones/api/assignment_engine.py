from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.asignacion_operaciones.schemas import AssignmentEngineResponse
from app.modules.asignacion_operaciones.services import AssignmentEngineConflictError, run_assignment_engine
from app.shared.dependencies.auth import get_current_operations_user

router = APIRouter(prefix="/operations", tags=["Operations"])

assignment_engine_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos operativos para ejecutar el motor de asignacion."},
    404: {"description": "Incidente no encontrado."},
    409: {"description": "El incidente no esta en estado pendiente para ser procesado."},
}


@router.post(
    "/incidents/{incident_id}/assignment-engine",
    response_model=AssignmentEngineResponse,
    responses=assignment_engine_responses,
)
def process_assignment_engine(
    incident_id: int,
    current_user: User = Depends(get_current_operations_user),
    db: Session = Depends(get_db),
) -> AssignmentEngineResponse:
    try:
        return AssignmentEngineResponse.model_validate(run_assignment_engine(db, incident_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AssignmentEngineConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
