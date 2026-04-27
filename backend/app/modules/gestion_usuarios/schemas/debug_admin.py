from pydantic import EmailStr, Field

from app.schemas.common import ORMBaseModel


class DebugAdminCreateRequest(ORMBaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class DebugAdminCreateResponse(ORMBaseModel):
    message: str
