from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Client
from app.modules.transacciones.schemas import PaymentCreateRequest, PaymentResponse
from app.modules.transacciones.services import create_incident_payment
from app.shared.dependencies.auth import get_current_client, get_incident_owned_by_current_client

router = APIRouter(prefix="/client/incidents", tags=["Client Payments"])

payment_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no pertenece a clients."},
    404: {"description": "Incidente o atencion no encontrada para el cliente autenticado."},
    409: {"description": "El servicio no puede pagarse o ya fue pagado."},
}


@router.post(
    "/{incident_id}/pay",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    responses=payment_responses,
)
def pay_incident_service(
    incident_id: int,
    data: PaymentCreateRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    incident = get_incident_owned_by_current_client(db, current_client, incident_id)

    try:
        payment = create_incident_payment(db, incident, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PaymentResponse.model_validate(payment)
