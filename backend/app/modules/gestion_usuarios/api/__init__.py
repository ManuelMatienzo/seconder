from fastapi import APIRouter

from app.modules.gestion_usuarios.api import (
    admin_incidents,
    admin_users,
    auth,
    clients,
    debug_admin,
    notifications,
    roles,
    technicians,
    users,
    vehicles,
    workshops,
)

router = APIRouter()
router.include_router(admin_incidents.router)
router.include_router(admin_users.router)
router.include_router(auth.router)
router.include_router(clients.router)
router.include_router(debug_admin.router)
router.include_router(notifications.router)
router.include_router(technicians.router)
router.include_router(vehicles.router)
router.include_router(workshops.router)
router.include_router(roles.router)
router.include_router(users.router)

__all__ = ["router"]
