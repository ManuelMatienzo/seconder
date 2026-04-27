from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id_assignment: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_incident: Mapped[int] = mapped_column(ForeignKey("incidents.id_incident"), nullable=False, index=True)
    id_workshop: Mapped[int] = mapped_column(ForeignKey("workshops.id_user"), nullable=False, index=True)
    id_technician: Mapped[int | None] = mapped_column(ForeignKey("technicians.id_technician"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    estimated_time_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    service_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    incident = relationship("Incident")
    workshop = relationship("Workshop")
    technician = relationship("Technician")
