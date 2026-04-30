from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.gestion_usuarios.models.user import User
from app.modules.asignacion_operaciones.schemas.assignment_history import AssignmentHistoryFilterParams, AssignmentHistoryItemResponse
from app.modules.asignacion_operaciones.services.assignment_history_service import get_workshop_history_detail, list_workshop_history
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
    items = list_workshop_history(db, current_user.id_user, filters)
    result = []
    for item in items:
        try:
            result.append(AssignmentHistoryItemResponse.model_validate(item))
        except Exception as exc:
            # En un entorno real usariamos logging.error
            print(f"Error validando item de historial {item.get('id_assignment')}: {exc}")
            continue
    return result


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


@router.get("/debug/clean")
def debug_clean_data(db: Session = Depends(get_db)):
    """Ruta temporal para limpiar datos de prueba que quedaron en el limbo."""
    from sqlalchemy import delete
    from app.modules.asignacion_operaciones.models.assignment import Assignment
    from app.modules.reporte_emergencias.models.incident import Incident
    from app.modules.reporte_emergencias.models.incident_photo import IncidentPhoto
    from app.modules.reporte_emergencias.models.incident_audio import IncidentAudio
    from app.modules.inteligencia_artificial.models.ai_analysis import AiAnalysis
    from app.modules.gestion_usuarios.models.notification import Notification
    from app.modules.transacciones.models.payment import Payment

    try:
        db.execute(delete(Payment))
        db.execute(delete(Assignment))
        db.execute(delete(IncidentPhoto))
        db.execute(delete(IncidentAudio))
        db.execute(delete(AiAnalysis))
        db.execute(delete(Notification))
        db.execute(delete(Incident))
        db.commit()
        return {"status": "success", "message": "Datos de emergencia eliminados correctamente. Refresca el dashboard."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
