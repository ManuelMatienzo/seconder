from datetime import datetime
from decimal import Decimal

from app.schemas.common import ORMBaseModel


class AdminIncidentResponse(ORMBaseModel):
    id_incident: int
    id_client: int
    id_vehicle: int
    latitude: Decimal
    longitude: Decimal
    description_text: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
