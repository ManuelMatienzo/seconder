from app.modules.gestion_usuarios.schemas.auth import LoginRequest, LoginResponse
from app.modules.gestion_usuarios.schemas.client import ClientRegisterRequest, ClientRegisterResponse, ClientResponse
from app.modules.gestion_usuarios.schemas.role import RoleResponse
from app.modules.gestion_usuarios.schemas.user import UserResponse
from app.modules.gestion_usuarios.schemas.vehicle import VehicleCreateRequest, VehicleResponse
from app.modules.gestion_usuarios.schemas.workshop import (
    WorkshopResponse,
    WorkshopTestRegisterRequest,
    WorkshopTestRegisterResponse,
    WorkshopUpsertRequest,
)

__all__ = [
    "ClientRegisterRequest",
    "ClientRegisterResponse",
    "ClientResponse",
    "LoginRequest",
    "LoginResponse",
    "RoleResponse",
    "UserResponse",
    "VehicleCreateRequest",
    "VehicleResponse",
    "WorkshopResponse",
    "WorkshopTestRegisterRequest",
    "WorkshopTestRegisterResponse",
    "WorkshopUpsertRequest",
]
