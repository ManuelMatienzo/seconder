from datetime import datetime
from typing import Literal

from app.schemas.common import ORMBaseModel


class AssignmentDecisionRequest(ORMBaseModel):
    decision: Literal["aceptado", "rechazado"]


class AssignmentDecisionResponse(ORMBaseModel):
    id_assignment: int
    id_incident: int
    id_workshop: int
    status: str
    accepted_at: datetime | None = None
    assigned_at: datetime | None = None
    incident_status: str
