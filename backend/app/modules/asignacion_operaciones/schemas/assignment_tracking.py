from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.schemas.common import ORMBaseModel


class AssignmentTrackingTechnicianResponse(ORMBaseModel):
    id_technician: int
    name: str
    phone: str | None = None
    specialty: str | None = None
    is_available: bool


class AssignmentTrackingWorkshopResponse(ORMBaseModel):
    id_workshop: int
    workshop_name: str


class AssignmentTrackingResponse(ORMBaseModel):
    id_assignment: int
    id_incident: int
    id_workshop: int
    id_technician: int | None = None
    status: str
    estimated_time_min: int | None = None
    distance_km: Decimal | None = None
    service_price: Decimal | None = None
    observations: str | None = None
    assigned_at: datetime
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    incident_status: str
    workshop: AssignmentTrackingWorkshopResponse
    technician: AssignmentTrackingTechnicianResponse | None = None


class AssignmentTrackingUpdateRequest(ORMBaseModel):
    status: Literal[
        "aceptado",
        "alistando",
        "en_ruta",
        "en_sitio",
        "completado",
        "cancelado",
        "en_camino",
    ] | None = None
    id_technician: int | None = None
    estimated_time_min: int | None = None
    distance_km: Decimal | None = None
    service_price: Decimal | None = None
    observations: str | None = None
