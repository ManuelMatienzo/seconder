from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import ORMBaseModel


class PaymentCreateRequest(ORMBaseModel):
    total_amount: Decimal = Field(gt=0)
    payment_method: Literal["efectivo", "tarjeta"]


class PaymentResponse(ORMBaseModel):
    id_payment: int
    id_assignment: int
    id_client: int
    total_amount: Decimal
    platform_commission: Decimal
    workshop_amount: Decimal
    payment_method: str
    payment_status: str
    created_at: datetime
