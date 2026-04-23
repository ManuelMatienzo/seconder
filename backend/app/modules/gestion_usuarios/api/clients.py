from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.gestion_usuarios.schemas import ClientRegisterRequest, ClientRegisterResponse
from app.modules.gestion_usuarios.services import register_client

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/register", response_model=ClientRegisterResponse, status_code=status.HTTP_201_CREATED)
def create_client_account(
    data: ClientRegisterRequest,
    db: Session = Depends(get_db),
) -> ClientRegisterResponse:
    try:
        client = register_client(db, data)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No se pudo conectar a PostgreSQL por un problema de codificacion "
                "en el mensaje de error del servidor. Verifica las credenciales y "
                "variables de entorno de la base de datos."
            ),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ClientRegisterResponse(message="Cliente registrado correctamente", client=client)
