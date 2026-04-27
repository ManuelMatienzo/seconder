from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.modules.gestion_usuarios.schemas import (
    NotificationReadResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.modules.gestion_usuarios.services import count_unread, get_user_notifications, mark_as_read
from app.shared.dependencies.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

notification_responses = {
    401: {"description": "No autenticado. Se requiere un token Bearer valido."},
    404: {"description": "Notificacion no encontrada para el usuario autenticado."},
}


@router.get("", response_model=list[NotificationResponse], responses=notification_responses)
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    return [NotificationResponse.model_validate(item) for item in get_user_notifications(db, current_user.id_user)]


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
    responses=notification_responses,
)
def patch_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationReadResponse:
    try:
        notification = mark_as_read(db, current_user.id_user, notification_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return NotificationReadResponse(
        id_notification=notification.id_notification,
        is_read=notification.is_read,
    )


@router.get("/unread/count", response_model=NotificationUnreadCountResponse, responses=notification_responses)
def get_unread_notifications_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationUnreadCountResponse:
    return NotificationUnreadCountResponse(unread_count=count_unread(db, current_user.id_user))
