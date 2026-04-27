from app.modules.gestion_usuarios.services.admin_incident_service import list_admin_incidents
from app.modules.gestion_usuarios.services.admin_user_service import (
    get_admin_user_detail,
    list_admin_users,
    update_admin_user_status,
)
from app.modules.gestion_usuarios.services.auth_service import authenticate_user
from app.modules.gestion_usuarios.services.client_service import get_client_by_id, register_client
from app.modules.gestion_usuarios.services.debug_admin_service import create_debug_admin
from app.modules.gestion_usuarios.services.notification_service import (
    count_unread,
    create_notification,
    get_user_notifications,
    mark_as_read,
)
from app.modules.gestion_usuarios.services.technician_service import (
    create_technician,
    get_workshop_technician_or_404,
    list_workshop_technicians,
    update_technician,
    update_technician_availability,
)
from app.modules.gestion_usuarios.services.vehicle_service import create_vehicle, list_client_vehicles
from app.modules.gestion_usuarios.services.workshop_service import (
    get_workshop_by_user_id,
    update_workshop_for_user,
    upsert_workshop_for_user,
)

__all__ = [
    "authenticate_user",
    "create_vehicle",
    "create_technician",
    "create_debug_admin",
    "get_admin_user_detail",
    "get_client_by_id",
    "get_user_notifications",
    "list_admin_incidents",
    "list_admin_users",
    "list_client_vehicles",
    "list_workshop_technicians",
    "count_unread",
    "create_notification",
    "mark_as_read",
    "register_client",
    "get_workshop_technician_or_404",
    "update_technician",
    "update_technician_availability",
    "update_admin_user_status",
    "get_workshop_by_user_id",
    "update_workshop_for_user",
    "upsert_workshop_for_user",
]
