from datetime import datetime

from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AiAnalysis(Base):
    __tablename__ = "ai_analyses"

    id_ai_analysis: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_incident: Mapped[int] = mapped_column(ForeignKey("incidents.id_incident"), nullable=False, unique=True, index=True)
    audio_transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'media'"),
    )
    severity_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    structured_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    incident = relationship("Incident", back_populates="ai_analysis")
