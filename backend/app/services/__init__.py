from app.modules.asignacion_operaciones.services import decide_available_request, list_available_requests
from app.modules.gestion_usuarios.services import (
    authenticate_user,
    create_vehicle,
    get_client_by_id,
    get_workshop_by_user_id,
    list_client_vehicles,
    register_client,
    update_workshop_for_user,
    upsert_workshop_for_user,
)
from app.modules.reporte_emergencias.services import (
    create_incident,
    create_incident_audio,
    create_incident_photo,
    get_incident_by_id,
    update_incident_description,
)

__all__ = [
    "authenticate_user",
    "create_incident",
    "create_incident_audio",
    "create_incident_photo",
    "create_vehicle",
    "decide_available_request",
    "list_available_requests",
    "get_client_by_id",
    "get_workshop_by_user_id",
    "get_incident_by_id",
    "list_client_vehicles",
    "register_client",
    "update_incident_description",
    "update_workshop_for_user",
    "upsert_workshop_for_user",
]
