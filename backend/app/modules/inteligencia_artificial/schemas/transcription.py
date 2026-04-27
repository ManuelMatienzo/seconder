from datetime import datetime

from app.schemas.common import ORMBaseModel


class TranscriptionSourceAudioResponse(ORMBaseModel):
    id_audio: int
    id_incident: int
    file_url: str
    format: str | None = None
    duration_seconds: int | None = None
    created_at: datetime


class IncidentTranscriptionResponse(ORMBaseModel):
    id_ai_analysis: int
    id_incident: int
    audio_transcription: str
    model_version: str | None = None
    created_at: datetime
    source_audio: TranscriptionSourceAudioResponse
