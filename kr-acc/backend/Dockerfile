FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS dev
RUN pip install --no-cache-dir .[dev]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
