from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id_payment: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_assignment: Mapped[int] = mapped_column(
        ForeignKey("assignments.id_assignment"),
        nullable=False,
        unique=True,
        index=True,
    )
    id_client: Mapped[int] = mapped_column(ForeignKey("clients.id_user"), nullable=False, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    platform_commission: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    workshop_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'completado'"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    assignment = relationship("Assignment")
    client = relationship("Client")
