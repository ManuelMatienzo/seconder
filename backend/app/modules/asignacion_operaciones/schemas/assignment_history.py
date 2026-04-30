from datetime import datetime, date
from decimal import Decimal

from app.schemas.common import ORMBaseModel


class AssignmentHistoryVehicleResponse(ORMBaseModel):
    id_vehicle: int
    license_plate: str | None = None
    plate: str
    brand: str
    model: str
    year: int | None = None
    color: str | None = None
    type: str | None = None


class AssignmentHistoryTechnicianResponse(ORMBaseModel):
    id_technician: int
    name: str
    phone: str | None = None
    specialty: str | None = None


class AssignmentHistoryAiAnalysisResponse(ORMBaseModel):
    audio_transcription: str | None = None
    classification: str | None = None
    priority_level: str | None = None
    structured_summary: str | None = None


class AssignmentHistoryItemResponse(ORMBaseModel):
    id_assignment: int
    id_incident: int
    status: str  # For Angular compatibility
    assignment_status: str
    incident_status: str
    assigned_at: datetime
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    estimated_time_min: int | None = None
    distance_km: Decimal | None = None
    service_price: Decimal | None = None
    observations: str | None = None
    payment_status: str | None = None
    client_name: str | None = None
    vehicle_summary: str | None = None
    technician_name: str | None = None
    incident_description: str | None = None
    photo_url: str | None = None
    audio_url: str | None = None
    client: dict | None = None
    vehicle: AssignmentHistoryVehicleResponse
    technician: AssignmentHistoryTechnicianResponse | None = None
    ai_analysis: AssignmentHistoryAiAnalysisResponse | None = None


class AssignmentHistoryFilterParams(ORMBaseModel):
    status: str | None = None
    id_technician: int | None = None
    date_from: date | None = None
    date_to: date | None = None
