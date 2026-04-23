from datetime import datetime

from pydantic import EmailStr

from app.modules.gestion_usuarios.schemas.role import RoleResponse
from app.schemas.common import ORMBaseModel


class UserResponse(ORMBaseModel):
    id_user: int
    name: str
    email: EmailStr
    phone: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    id_role: int
    role: RoleResponse | None = None
