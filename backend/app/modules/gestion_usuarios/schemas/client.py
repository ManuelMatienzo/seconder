from datetime import datetime

from pydantic import EmailStr, Field

from app.modules.gestion_usuarios.schemas.user import UserResponse
from app.schemas.common import ORMBaseModel


class ClientRegisterRequest(ORMBaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)


class ClientUpdateRequest(ORMBaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)


class ClientAdminResponse(ORMBaseModel):
    id_user: int
    name: str
    email: str
    phone: str | None = None
    status: str
    created_at: datetime


class ClientResponse(ORMBaseModel):
    id_user: int
    user: UserResponse | None = None


class ClientRegisterResponse(ORMBaseModel):
    message: str
    client: ClientResponse
