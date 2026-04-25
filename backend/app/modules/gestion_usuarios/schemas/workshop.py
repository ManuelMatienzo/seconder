from decimal import Decimal

from pydantic import Field

from app.schemas.common import ORMBaseModel


class WorkshopTestRegisterRequest(ORMBaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)


class WorkshopTestRegisterResponse(ORMBaseModel):
    message: str
    id_user: int
    email: str
    id_role: int


class WorkshopUpsertRequest(ORMBaseModel):
    workshop_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    phone: str | None = Field(default=None, max_length=20)
    specialties: str | None = None
    is_available: bool


class WorkshopResponse(ORMBaseModel):
    id_user: int
    workshop_name: str
    address: str
    latitude: Decimal
    longitude: Decimal
    phone: str | None = None
    specialties: str | None = None
    is_available: bool
    rating: float | None = None
