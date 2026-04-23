from fastapi import APIRouter

from app.modules.gestion_usuarios.api import auth, clients, roles, users, vehicles

router = APIRouter()
router.include_router(auth.router)
router.include_router(clients.router)
router.include_router(vehicles.router)
router.include_router(roles.router)
router.include_router(users.router)

__all__ = ["router"]
