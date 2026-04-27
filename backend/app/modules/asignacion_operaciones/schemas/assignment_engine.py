from app.schemas.common import ORMBaseModel


class AssignmentEngineIncidentContextResponse(ORMBaseModel):
    id_incident: int
    id_client: int
    id_vehicle: int
    incident_status: str
    latitude: float
    longitude: float
    description_text: str | None = None


class AssignmentEngineAiContextResponse(ORMBaseModel):
    classification: str | None = None
    priority_level: str | None = None
    structured_summary: str | None = None


class AssignmentEngineWorkshopRecommendationResponse(ORMBaseModel):
    id_workshop: int
    workshop_name: str
    is_available: bool
    distance_km: float
    estimated_time_min: int
    rating: float | None = None
    specialties: str | None = None
    score: float
    reason: str


class AssignmentEngineResponse(ORMBaseModel):
    id_incident: int
    incident_status: str
    classification: str | None = None
    priority_level: str | None = None
    structured_summary: str | None = None
    incident: AssignmentEngineIncidentContextResponse
    recommended_workshops: list[AssignmentEngineWorkshopRecommendationResponse]
