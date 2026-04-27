from app.schemas.common import ORMBaseModel


class IncidentSummarySourcesResponse(ORMBaseModel):
    description_text: bool
    audio_transcription: bool
    classification: bool
    priority_level: bool
    vehicle_data: bool


class IncidentSummaryResponse(ORMBaseModel):
    id_ai_analysis: int
    id_incident: int
    structured_summary: str
    model_version: str
    sources_used: IncidentSummarySourcesResponse
