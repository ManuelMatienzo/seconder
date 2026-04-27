from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(db: Session, id_user: int, title: str, message: str, type: str) -> Notification:
    notification = Notification(
        id_user=id_user,
        title=title,
        message=message,
        type=type,
        is_read=False,
    )
    db.add(notification)
    return notification


def get_user_notifications(db: Session, id_user: int) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.id_user == id_user)
        .order_by(Notification.created_at.desc(), Notification.id_notification.desc())
    )
    return list(db.scalars(stmt))


def mark_as_read(db: Session, id_user: int, notification_id: int) -> Notification:
    notification = db.scalar(
        select(Notification).where(
            Notification.id_notification == notification_id,
            Notification.id_user == id_user,
        )
    )
    if not notification:
        raise LookupError("Notificacion no encontrada")

    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def count_unread(db: Session, id_user: int) -> int:
    stmt = select(func.count(Notification.id_notification)).where(
        Notification.id_user == id_user,
        Notification.is_read.is_(False),
    )
    return db.scalar(stmt) or 0
