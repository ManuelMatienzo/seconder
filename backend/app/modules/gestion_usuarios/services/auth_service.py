from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.modules.gestion_usuarios.schemas import LoginRequest
from app.shared.security.security import verify_password


def authenticate_user(db: Session, data: LoginRequest) -> User | None:
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or user.status != "activo":
        return None

    if not verify_password(data.password, user.password_hash):
        return None

    return user
