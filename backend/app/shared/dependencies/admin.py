from fastapi import Depends, HTTPException, status

from app.models import User
from app.shared.dependencies.auth import get_current_user


ADMIN_ROLE_ID = 1


def require_admin(user: User) -> User:
    if user.id_role == ADMIN_ROLE_ID:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="El usuario autenticado no tiene permisos de administrador",
    )


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    return require_admin(current_user)
