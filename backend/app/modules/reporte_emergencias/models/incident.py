from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id_incident: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_client: Mapped[int] = mapped_column(ForeignKey("clients.id_user"), nullable=False, index=True)
    id_vehicle: Mapped[int] = mapped_column(ForeignKey("vehicles.id_vehicle"), nullable=False, index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'pendiente'"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    client = relationship("Client", back_populates="incidents")
    vehicle = relationship("Vehicle", back_populates="incidents")
    photos = relationship("IncidentPhoto", back_populates="incident")
    audios = relationship("IncidentAudio", back_populates="incident")
    ai_analysis = relationship("AiAnalysis", back_populates="incident", uselist=False)
