from app.modules.gestion_usuarios.services import (
    authenticate_user,
    create_vehicle,
    get_client_by_id,
    list_client_vehicles,
    register_client,
)
from app.modules.reporte_emergencias.services import (
    create_incident,
    create_incident_audio,
    create_incident_photo,
    get_incident_by_id,
)

__all__ = [
    "authenticate_user",
    "create_incident",
    "create_incident_audio",
    "create_incident_photo",
    "create_vehicle",
    "get_client_by_id",
    "get_incident_by_id",
    "list_client_vehicles",
    "register_client",
]
