# sport-api

Microservicio de la plataforma [juan-in-one](https://github.com/juan-in-one) — retos deportivos (carreras,
ultras, montaña), cumplidos y pendientes, con récords personales.

Stack: Python + FastAPI + SQLAlchemy (async) + PostgreSQL. Instrumentado con OpenTelemetry (métricas +
trazas) desde el primer commit.

Segundo microservicio de la plataforma, réplica deliberada del patrón de `car-api` (mismo Dockerfile, mismo
chart de Helm, mismo pipeline) — sirvió para confirmar que el patrón se puede reutilizar de verdad en un
dominio distinto sin tocar la plataforma compartida (Postgres, Vault, observabilidad), solo añadiendo las
piezas propias del microservicio.

## Modelo de datos

Un único tipo, **`Challenge`**: un reto deportivo, con `category` (`race` / `mountain`) y `status`
(`pending` / `completed`) independientes — un reto de montaña pendiente y una carrera ya conseguida se
consultan igual, filtrando por el campo que toque. Incluye distancia, desnivel y resultado, todos
opcionales (no todos los retos tienen los mismos datos: una ruta de montaña no tiene "resultado" en el
sentido de una carrera cronometrada).

## Desarrollo local

```bash
cp .env.example .env
docker compose up --build
```

API disponible en `http://localhost:8001` (docs interactivas en `/docs`).

## Tests

```bash
pip install -r requirements-check.txt
pytest --cov=app
```

## Endpoints

- `GET /health`
- `POST /challenges`
- `GET /challenges`
- `GET /challenges/{id}`
- `DELETE /challenges/{id}`

## CI/CD

- **`pr-checks.yml`** corre en cada PR: lint (Ruff), tests con cobertura, Gitleaks, Dependency Review, y un
  build + escaneo de la imagen de prueba que **no puede publicar nada** — no hay ni login a GHCR en ese
  workflow.
- **`ci.yml`** corre solo al fusionar a `main`: los mismos escaneos (bloqueantes: Trivy, Semgrep, ZAP),
  build, firma de la imagen con Cosign (keyless) + SBOM con Syft, y publicación en GHCR.
- `main` está protegida: solo se puede fusionar vía PR desde una rama `feat/*`, con los checks de arriba en
  verde.

Ver [juan-in-one/.github](https://github.com/juan-in-one/.github) para el workflow reutilizable completo, y
el [README de la organización](https://github.com/juan-in-one) para la arquitectura de toda la plataforma
(GitOps, cadena de suministro firmada, observabilidad).
