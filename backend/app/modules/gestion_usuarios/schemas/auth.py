from pydantic import EmailStr, Field

from app.modules.gestion_usuarios.schemas.user import UserResponse
from app.schemas.common import ORMBaseModel


class LoginRequest(ORMBaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(ORMBaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
