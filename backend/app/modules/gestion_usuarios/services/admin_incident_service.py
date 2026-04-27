from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Incident


def list_admin_incidents(db: Session) -> list[Incident]:
    stmt = select(Incident).order_by(Incident.created_at.desc(), Incident.id_incident.desc())
    return list(db.scalars(stmt))
