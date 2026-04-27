from datetime import datetime

from app.schemas.common import ORMBaseModel


class NotificationResponse(ORMBaseModel):
    id_notification: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationReadResponse(ORMBaseModel):
    id_notification: int
    is_read: bool


class NotificationUnreadCountResponse(ORMBaseModel):
    unread_count: int
