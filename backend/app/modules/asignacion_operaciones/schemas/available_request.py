from datetime import datetime
from decimal import Decimal

from app.schemas.common import ORMBaseModel


class AvailableRequestClientResponse(ORMBaseModel):
    id_client: int
    name: str
    phone: str | None = None


class AvailableRequestVehicleResponse(ORMBaseModel):
    id_vehicle: int
    license_plate: str
    brand: str
    model: str
    year: int | None = None
    color: str | None = None
    type: str | None = None


class AvailableRequestAiDataResponse(ORMBaseModel):
    audio_transcription: str | None = None
    classification: str | None = None
    priority_level: str | None = None
    structured_summary: str | None = None


class AvailableRequestResponse(ORMBaseModel):
    id_incident: int
    id_client: int
    id_vehicle: int
    latitude: Decimal
    longitude: Decimal
    description_text: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    photo_url: str | None = None
    audio_url: str | None = None
    client: AvailableRequestClientResponse | None = None
    vehicle: AvailableRequestVehicleResponse | None = None
    ai_analysis: AvailableRequestAiDataResponse | None = None
