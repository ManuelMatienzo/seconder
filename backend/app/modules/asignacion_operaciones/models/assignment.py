from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id_incident: Mapped[int] = mapped_column(ForeignKey("incidents.id_incident"), primary_key=True, index=True)
    id_workshop: Mapped[int] = mapped_column(ForeignKey("workshops.id_user"), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
