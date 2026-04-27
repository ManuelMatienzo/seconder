from decimal import Decimal

from app.schemas.common import ORMBaseModel


class ClientIncidentStatusWorkshopResponse(ORMBaseModel):
    id_workshop: int
    workshop_name: str
    phone: str | None = None


class ClientIncidentStatusTechnicianResponse(ORMBaseModel):
    id_technician: int
    name: str
    phone: str | None = None
    specialty: str | None = None


class ClientIncidentStatusResponse(ORMBaseModel):
    id_incident: int
    incident_status: str
    assignment_status: str | None = None
    priority_level: str | None = None
    estimated_time_min: int | None = None
    distance_km: Decimal | None = None
    workshop: ClientIncidentStatusWorkshopResponse | None = None
    technician: ClientIncidentStatusTechnicianResponse | None = None
