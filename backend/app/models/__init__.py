from app.modules.asignacion_operaciones.models import Assignment
from app.modules.gestion_usuarios.models import Client, Role, User, Vehicle, Workshop
from app.modules.inteligencia_artificial.models import AiAnalysis
from app.modules.reporte_emergencias.models import Incident, IncidentAudio, IncidentPhoto

__all__ = [
    "Assignment",
    "AiAnalysis",
    "Client",
    "Incident",
    "IncidentAudio",
    "IncidentPhoto",
    "Role",
    "User",
    "Vehicle",
    "Workshop",
]
