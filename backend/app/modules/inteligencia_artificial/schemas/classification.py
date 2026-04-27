from datetime import datetime

from app.schemas.common import ORMBaseModel


class ClassificationSourcePhotoResponse(ORMBaseModel):
    id_photo: int
    id_incident: int
    file_url: str
    format: str | None = None
    size_kb: int | None = None
    created_at: datetime


class IncidentClassificationResponse(ORMBaseModel):
    id_ai_analysis: int
    id_incident: int
    classification: str
    model_version: str | None = None
    created_at: datetime
    source_photo: ClassificationSourcePhotoResponse
