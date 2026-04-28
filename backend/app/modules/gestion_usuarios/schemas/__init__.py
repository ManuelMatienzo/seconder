from app.modules.gestion_usuarios.schemas.admin_incident import AdminIncidentResponse
from app.modules.gestion_usuarios.schemas.admin_user import (
    AdminUserClientDataResponse,
    AdminUserDetailResponse,
    AdminUserListItemResponse,
    AdminUserStatusUpdateRequest,
    AdminUserStatusUpdateResponse,
    AdminUserWorkshopDataResponse,
)
from app.modules.gestion_usuarios.schemas.auth import LoginRequest, LoginResponse
from app.modules.gestion_usuarios.schemas.client import ClientRegisterRequest, ClientRegisterResponse, ClientResponse
from app.modules.gestion_usuarios.schemas.debug_admin import DebugAdminCreateRequest, DebugAdminCreateResponse
from app.modules.gestion_usuarios.schemas.notification import (
    NotificationReadResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.modules.gestion_usuarios.schemas.role import RoleResponse
from app.modules.gestion_usuarios.schemas.technician import (
    TechnicianAvailabilityUpdateRequest,
    TechnicianCreateRequest,
    TechnicianResponse,
    TechnicianUpdateRequest,
)
from app.modules.gestion_usuarios.schemas.user import UserResponse
from app.modules.gestion_usuarios.schemas.vehicle import VehicleCreateRequest, VehicleResponse
from app.modules.gestion_usuarios.schemas.workshop import (
    WorkshopAccountCreateRequest,
    WorkshopAdminUpsertRequest,
    WorkshopResponse,
    WorkshopUpsertRequest,
)

__all__ = [
    "AdminIncidentResponse",
    "AdminUserClientDataResponse",
    "AdminUserDetailResponse",
    "AdminUserListItemResponse",
    "AdminUserStatusUpdateRequest",
    "AdminUserStatusUpdateResponse",
    "AdminUserWorkshopDataResponse",
    "ClientRegisterRequest",
    "ClientRegisterResponse",
    "ClientResponse",
    "DebugAdminCreateRequest",
    "DebugAdminCreateResponse",
    "NotificationReadResponse",
    "NotificationResponse",
    "NotificationUnreadCountResponse",
    "LoginRequest",
    "LoginResponse",
    "RoleResponse",
    "TechnicianAvailabilityUpdateRequest",
    "TechnicianCreateRequest",
    "TechnicianResponse",
    "TechnicianUpdateRequest",
    "UserResponse",
    "VehicleCreateRequest",
    "VehicleResponse",
    "WorkshopAccountCreateRequest",
    "WorkshopAdminUpsertRequest",
    "WorkshopResponse",
    "WorkshopUpsertRequest",
]
