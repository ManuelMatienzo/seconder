from app.schemas.common import ORMBaseModel


class IncidentPrioritySignalsResponse(ORMBaseModel):
    description_text: str | None = None
    classification: str | None = None
    audio_transcription_used: bool


class IncidentPriorityResponse(ORMBaseModel):
    id_ai_analysis: int
    id_incident: int
    priority_level: str
    severity_score: int
    model_version: str
    signals_used: IncidentPrioritySignalsResponse
