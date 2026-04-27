from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.transacciones.schemas import (
    CommissionFilterParams,
    CommissionItemResponse,
    CommissionSummaryResponse,
)
from app.modules.transacciones.services import get_commissions_summary, list_commissions
from app.shared.dependencies.auth import get_current_admin_user

router = APIRouter(prefix="/admin/commissions", tags=["Admin Commissions"])

commission_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    403: {"description": "El usuario autenticado no tiene permisos de administrador."},
}


@router.get("", response_model=list[CommissionItemResponse], responses=commission_responses)
def get_commissions(
    date_from: date | None = None,
    date_to: date | None = None,
    payment_status: str | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> list[CommissionItemResponse]:
    _ = current_user
    filters = CommissionFilterParams(
        date_from=date_from,
        date_to=date_to,
        payment_status=payment_status,
    )
    return [CommissionItemResponse.model_validate(item) for item in list_commissions(db, filters)]


@router.get("/summary", response_model=CommissionSummaryResponse, responses=commission_responses)
def get_commissions_summary_view(
    date_from: date | None = None,
    date_to: date | None = None,
    payment_status: str | None = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> CommissionSummaryResponse:
    _ = current_user
    filters = CommissionFilterParams(
        date_from=date_from,
        date_to=date_to,
        payment_status=payment_status,
    )
    return CommissionSummaryResponse.model_validate(get_commissions_summary(db, filters))
