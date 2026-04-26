from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.inteligencia_artificial.schemas import IncidentClassificationResponse
from app.modules.inteligencia_artificial.services import ClassificationProviderError, classify_incident_photo
from app.shared.dependencies.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

classification_responses = {
    400: {"description": "El incidente no tiene fotos asociadas para clasificar."},
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos sobre este incidente."},
    404: {"description": "Incidente no encontrado."},
    502: {"description": "No se pudo acceder a la imagen o al proveedor de clasificacion externo."},
}


@router.post(
    "/incidents/{incident_id}/classification",
    response_model=IncidentClassificationResponse,
    status_code=status.HTTP_200_OK,
    responses=classification_responses,
)
def execute_incident_classification(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IncidentClassificationResponse:
    try:
        return IncidentClassificationResponse.model_validate(
            classify_incident_photo(db, incident_id, current_user)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ClassificationProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
