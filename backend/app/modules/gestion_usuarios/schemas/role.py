from app.schemas.common import ORMBaseModel


class RoleResponse(ORMBaseModel):
    id_role: int
    name: str
    description: str | None = None
