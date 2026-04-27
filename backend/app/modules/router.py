from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.asignacion_operaciones.api import router as asignacion_operaciones_router
from app.modules.gestion_usuarios.api import router as gestion_usuarios_router
from app.modules.reporte_emergencias.api import router as reporte_emergencias_router
from app.modules.transacciones.api import router as transacciones_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(gestion_usuarios_router)
api_router.include_router(reporte_emergencias_router)
api_router.include_router(asignacion_operaciones_router)
api_router.include_router(transacciones_router)

__all__ = ["api_router"]
