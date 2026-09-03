import uuid

from fastapi import Depends, FastAPI, HTTPException
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import make_asgi_app
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db
from app.models import Challenge
from app.schemas import ChallengeCreate, ChallengeOut

app = FastAPI(title=settings.app_name)

# Métricas de aplicación con OpenTelemetry — mismo patrón que car-api (ver
# app/main.py allí y wiki/log.md 2026-09-03 para el porqué de cada pieza).
metrics.set_meter_provider(
    MeterProvider(
        metric_readers=[PrometheusMetricReader()],
        resource=Resource.create({"service.name": "sport-api"}),
    )
)
meter = metrics.get_meter("sport-api")

# excluded_urls: /health (sondas de Kubernetes) y /metrics (el propio
# Prometheus scrapeándose a sí mismo) no son tráfico de negocio real — ver el
# hallazgo real en car-api (log.md 2026-09-03) antes de que hiciera falta
# corregirlo ahí a posteriori.
FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/metrics")

app.mount("/metrics", make_asgi_app())

challenges_created = meter.create_counter(
    name="sport_challenges_created_total",
    description="Retos creados",
)


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
    challenges_created.add(1)
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


@app.delete("/challenges/{challenge_id}", status_code=204)
async def delete_challenge(challenge_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    challenge = await db.get(Challenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    await db.delete(challenge)
    await db.commit()
