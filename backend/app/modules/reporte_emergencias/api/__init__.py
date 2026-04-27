from fastapi import APIRouter

from app.modules.reporte_emergencias.api import incident_audios, incident_photos, incidents

router = APIRouter()
router.include_router(incidents.router)
router.include_router(incident_photos.router)
router.include_router(incident_audios.router)

__all__ = ["router"]
