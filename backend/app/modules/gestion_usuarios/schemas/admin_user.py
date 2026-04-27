from decimal import Decimal
from typing import Literal

from app.schemas.common import ORMBaseModel


class AdminUserListItemResponse(ORMBaseModel):
    id_user: int
    email: str
    role: str | None = None
    is_active: bool
    status: str


class AdminUserClientDataResponse(ORMBaseModel):
    id_user: int


class AdminUserWorkshopDataResponse(ORMBaseModel):
    id_user: int
    workshop_name: str
    address: str
    latitude: Decimal
    longitude: Decimal
    phone: str | None = None
    specialties: str | None = None
    is_available: bool
    rating: float | None = None


class AdminUserDetailResponse(ORMBaseModel):
    id_user: int
    email: str
    role: str | None = None
    is_active: bool
    status: str
    type: str | None = None
    client: AdminUserClientDataResponse | None = None
    workshop: AdminUserWorkshopDataResponse | None = None


class AdminUserStatusUpdateRequest(ORMBaseModel):
    status: Literal["activo", "bloqueado"]


class AdminUserStatusUpdateResponse(ORMBaseModel):
    id_user: int
    status: str
    is_active: bool
