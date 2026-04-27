from importlib import import_module

_EXPORTS = {
    "ClientRegisterRequest": "app.modules.gestion_usuarios.schemas.client",
    "ClientRegisterResponse": "app.modules.gestion_usuarios.schemas.client",
    "ClientResponse": "app.modules.gestion_usuarios.schemas.client",
    "LoginRequest": "app.modules.gestion_usuarios.schemas.auth",
    "LoginResponse": "app.modules.gestion_usuarios.schemas.auth",
    "RoleResponse": "app.modules.gestion_usuarios.schemas.role",
    "UserResponse": "app.modules.gestion_usuarios.schemas.user",
    "VehicleCreateRequest": "app.modules.gestion_usuarios.schemas.vehicle",
    "VehicleResponse": "app.modules.gestion_usuarios.schemas.vehicle",
    "WorkshopResponse": "app.modules.gestion_usuarios.schemas.workshop",
    "WorkshopUpsertRequest": "app.modules.gestion_usuarios.schemas.workshop",
    "AvailableRequestAiDataResponse": "app.modules.asignacion_operaciones.schemas.available_request",
    "AvailableRequestResponse": "app.modules.asignacion_operaciones.schemas.available_request",
    "AvailableRequestVehicleResponse": "app.modules.asignacion_operaciones.schemas.available_request",
    "AssignmentDecisionRequest": "app.modules.asignacion_operaciones.schemas.assignment_decision",
    "AssignmentDecisionResponse": "app.modules.asignacion_operaciones.schemas.assignment_decision",
    "IncidentAudioCreateRequest": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentAudioResponse": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentCreateRequest": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentDescriptionUpdateRequest": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentPhotoCreateRequest": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentPhotoResponse": "app.modules.reporte_emergencias.schemas.incident",
    "IncidentResponse": "app.modules.reporte_emergencias.schemas.incident",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'app.schemas' has no attribute '{name}'")

    module = import_module(module_name)
    return getattr(module, name)
