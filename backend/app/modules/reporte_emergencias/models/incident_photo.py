from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IncidentPhoto(Base):
    __tablename__ = "incident_photos"

    id_photo: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_incident: Mapped[int] = mapped_column(ForeignKey("incidents.id_incident"), nullable=False, index=True)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str | None] = mapped_column(String(10), nullable=True)
    size_kb: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    incident = relationship("Incident", back_populates="photos")
