import uuid

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db
from app.models import Challenge
from app.schemas import ChallengeCreate, ChallengeOut

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/challenges", response_model=ChallengeOut, status_code=201)
async def create_challenge(
    payload: ChallengeCreate, db: AsyncSession = Depends(get_db)
) -> Challenge:
    challenge = Challenge(**payload.model_dump())
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)
    return challenge


@app.get("/challenges", response_model=list[ChallengeOut])
async def list_challenges(db: AsyncSession = Depends(get_db)) -> list[Challenge]:
    result = await db.execute(select(Challenge).order_by(Challenge.challenge_date.desc()))
    return list(result.scalars().all())


@app.get("/challenges/{challenge_id}", response_model=ChallengeOut)
async def get_challenge(challenge_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Challenge:
    challenge = await db.get(Challenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge
