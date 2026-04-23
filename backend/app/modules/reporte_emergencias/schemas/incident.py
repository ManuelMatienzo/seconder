from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import ORMBaseModel


class IncidentPhotoCreateRequest(ORMBaseModel):
    id_incident: int | None = None
    file_url: str = Field(min_length=1)
    format: str | None = Field(default=None, max_length=10)
    size_kb: int | None = Field(default=None, ge=0)


class IncidentAudioCreateRequest(ORMBaseModel):
    id_incident: int | None = None
    file_url: str = Field(min_length=1)
    format: str | None = Field(default=None, max_length=10)
    duration_seconds: int | None = Field(default=None, ge=0)


class IncidentCreateRequest(ORMBaseModel):
    id_vehicle: int
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    description_text: str | None = None
    photos: list[IncidentPhotoCreateRequest] = Field(
        default_factory=list,
        description="Opcional. Evidencias fotograficas para registrar junto al incidente.",
    )
    audios: list[IncidentAudioCreateRequest] = Field(
        default_factory=list,
        description="Opcional. Evidencias de audio para registrar junto al incidente.",
    )


class IncidentPhotoResponse(ORMBaseModel):
    id_photo: int
    id_incident: int
    file_url: str
    format: str | None = None
    size_kb: int | None = None
    created_at: datetime


class IncidentAudioResponse(ORMBaseModel):
    id_audio: int
    id_incident: int
    file_url: str
    format: str | None = None
    duration_seconds: int | None = None
    created_at: datetime


class IncidentResponse(ORMBaseModel):
    id_incident: int
    id_client: int
    id_vehicle: int
    latitude: Decimal
    longitude: Decimal
    description_text: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    photos: list[IncidentPhotoResponse] = Field(default_factory=list)
    audios: list[IncidentAudioResponse] = Field(default_factory=list)
