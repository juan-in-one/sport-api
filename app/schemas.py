import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models import ChallengeCategory, ChallengeStatus


class ChallengeBase(BaseModel):
    category: ChallengeCategory
    status: ChallengeStatus = ChallengeStatus.pending
    name: str
    location: str | None = None
    challenge_date: date
    distance_km: float | None = None
    elevation_m: int | None = None
    result: str | None = None
    notes: str | None = None


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeOut(ChallengeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
