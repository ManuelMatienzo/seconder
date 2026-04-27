from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.gestion_usuarios.schemas import DebugAdminCreateRequest, DebugAdminCreateResponse
from app.modules.gestion_usuarios.services import create_debug_admin

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post(
    "/create-admin",
    response_model=DebugAdminCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "El rol admin no existe en la base de datos."},
        409: {"description": "Ya existe un usuario con ese email."},
    },
)
def create_admin_debug(
    data: DebugAdminCreateRequest,
    db: Session = Depends(get_db),
) -> DebugAdminCreateResponse:
    try:
        create_debug_admin(db, data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return DebugAdminCreateResponse(message="admin creado correctamente")
