from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBaseModel


class TechnicianCreateRequest(ORMBaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    specialty: str | None = Field(default=None, max_length=100)
    is_available: bool = True


class TechnicianUpdateRequest(ORMBaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    specialty: str | None = Field(default=None, max_length=100)
    is_available: bool


class TechnicianAvailabilityUpdateRequest(ORMBaseModel):
    is_available: bool


class TechnicianResponse(ORMBaseModel):
    id_technician: int
    id_workshop: int
    name: str
    phone: str | None = None
    specialty: str | None = None
    is_available: bool
    created_at: datetime
