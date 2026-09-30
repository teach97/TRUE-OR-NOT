# Backend production image (FastAPI). Used only for hosted deploys;
# local development keeps using `uv run uvicorn main:app ...`.
FROM python:3.12-slim AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache
COPY . ./
EXPOSE 8010
CMD ["sh", "-c", ".venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8010}"]
