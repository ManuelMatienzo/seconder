
from fastapi import APIRouter

from app.modules.inteligencia_artificial.api.classifications import router as classifications_router
from app.modules.inteligencia_artificial.api.transcriptions import router as transcriptions_router

router = APIRouter()
router.include_router(classifications_router)
router.include_router(transcriptions_router)

__all__ = ["router"]
