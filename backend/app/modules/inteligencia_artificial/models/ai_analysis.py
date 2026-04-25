from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AiAnalysis(Base):
    __tablename__ = "ai_analyses"

    id_incident: Mapped[int] = mapped_column(ForeignKey("incidents.id_incident"), primary_key=True, index=True)
    audio_transcription: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    incident = relationship("Incident")
