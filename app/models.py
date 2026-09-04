import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ChallengeCategory(str, enum.Enum):
    race = "race"
    mountain = "mountain"


class ChallengeStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class Challenge(Base):
    """Un reto deportivo: una carrera/ultra o una ruta/pico de montaña,
    ya conseguido o pendiente como objetivo futuro."""

    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[ChallengeCategory] = mapped_column(
        Enum(ChallengeCategory, name="challenge_category"), nullable=False
    )
    status: Mapped[ChallengeStatus] = mapped_column(
        Enum(ChallengeStatus, name="challenge_status"),
        nullable=False,
        default=ChallengeStatus.pending,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    challenge_date: Mapped[date] = mapped_column(Date, nullable=False)
    distance_km: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    elevation_m: Mapped[int | None] = mapped_column(nullable=True)
    result: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
