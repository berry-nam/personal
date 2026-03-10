FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "-m", "prefect", "worker", "start", "--pool", "default"]

FROM base AS dev
RUN pip install --no-cache-dir .[dev]
CMD ["python", "-m", "prefect", "worker", "start", "--pool", "default"]
