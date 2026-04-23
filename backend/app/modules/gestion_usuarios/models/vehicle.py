from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id_vehicle: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_client: Mapped[int] = mapped_column(ForeignKey("clients.id_user"), nullable=False, index=True)
    plate: Mapped[str] = mapped_column(String(15), nullable=False, unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int | None] = mapped_column(nullable=True)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    client = relationship("Client", back_populates="vehicles")
    incidents = relationship("Incident", back_populates="vehicle")
