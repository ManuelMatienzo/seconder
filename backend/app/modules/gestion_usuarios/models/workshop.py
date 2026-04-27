from decimal import Decimal

from sqlalchemy import Boolean, Float, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Workshop(Base):
    __tablename__ = "workshops"

    id_user: Mapped[int] = mapped_column(ForeignKey("users.id_user"), primary_key=True, index=True)
    workshop_name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    specialties: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship("User", back_populates="workshop")
    technicians = relationship("Technician", back_populates="workshop")
