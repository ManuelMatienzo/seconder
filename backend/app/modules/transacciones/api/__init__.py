
from fastapi import APIRouter

from app.modules.transacciones.api.commissions import router as commissions_router
from app.modules.transacciones.api.payment import router as payment_router

router = APIRouter()
router.include_router(commissions_router)
router.include_router(payment_router)

__all__ = ["router"]
