
from fastapi import APIRouter

from app.modules.asignacion_operaciones.api.assignment_engine import router as assignment_engine_router
from app.modules.asignacion_operaciones.api.assignments import router as assignments_router
from app.modules.asignacion_operaciones.api.available_requests import router as available_requests_router

router = APIRouter()
router.include_router(assignment_engine_router)
router.include_router(available_requests_router)
router.include_router(assignments_router)

__all__ = ["router"]
