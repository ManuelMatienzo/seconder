from decimal import Decimal

from pydantic import EmailStr, Field

from app.schemas.common import ORMBaseModel


class WorkshopUpsertRequest(ORMBaseModel):
    workshop_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    phone: str | None = Field(default=None, max_length=20)
    specialties: str | None = None
    is_available: bool


class WorkshopAccountCreateRequest(WorkshopUpsertRequest):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class WorkshopAdminUpsertRequest(WorkshopUpsertRequest):
    id_user: int = Field(ge=1)


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
