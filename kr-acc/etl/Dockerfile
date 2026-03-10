# ── Dev stage ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS dev

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]"
COPY . .
CMD ["python", "-m", "prefect", "worker", "start", "--pool", "default"]

# ── Production stage ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS prod

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY . .
CMD ["python", "-m", "prefect", "worker", "start", "--pool", "default"]
