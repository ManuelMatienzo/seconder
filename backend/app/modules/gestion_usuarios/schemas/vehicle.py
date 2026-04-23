from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBaseModel


class VehicleCreateRequest(ORMBaseModel):
    plate: str = Field(min_length=3, max_length=15)
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=30)
    type: str | None = Field(default=None, max_length=30)


class VehicleResponse(ORMBaseModel):
    id_vehicle: int
    id_client: int
    plate: str
    brand: str
    model: str
    year: int | None = None
    color: str | None = None
    type: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
