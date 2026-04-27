from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import ORMBaseModel


class CommissionItemResponse(ORMBaseModel):
    id_payment: int
    id_assignment: int
    total_amount: Decimal
    platform_commission: Decimal
    workshop_amount: Decimal
    payment_method: str
    payment_status: str
    created_at: datetime


class CommissionSummaryResponse(ORMBaseModel):
    total_transactions: int
    total_amount: Decimal
    total_commission: Decimal
    total_workshop_earnings: Decimal


class CommissionFilterParams(ORMBaseModel):
    date_from: date | None = None
    date_to: date | None = None
    payment_status: str | None = None
