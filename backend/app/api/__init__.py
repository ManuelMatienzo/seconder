from fastapi import APIRouter

from app.api import auth, clients, health, incident_audios, incident_photos, incidents, roles, users, vehicles

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(vehicles.router)
api_router.include_router(incidents.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(incident_photos.router)
api_router.include_router(incident_audios.router)

__all__ = ["api_router"]
