from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id_user: Mapped[int] = mapped_column(ForeignKey("users.id_user"), primary_key=True, index=True)

    user = relationship("User", back_populates="client")
    vehicles = relationship("Vehicle", back_populates="client")
    incidents = relationship("Incident", back_populates="client")
