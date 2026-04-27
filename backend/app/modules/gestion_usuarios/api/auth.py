from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.gestion_usuarios.schemas import LoginRequest, LoginResponse, UserResponse
from app.modules.gestion_usuarios.services import authenticate_user
from app.shared.dependencies.auth import get_current_user
from app.shared.security.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = authenticate_user(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    access_token = create_access_token(subject=str(user.id_user))
    return LoginResponse(message="Login correcto", access_token=access_token, user=user)


@router.get("/me", response_model=UserResponse)
def get_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
