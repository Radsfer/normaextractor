# ---------------------------------------------------------------------------
# NormaExtractor — imagem única (frontend build + backend FastAPI)
# Stage 1: build da SPA React
# Stage 2: backend Python (llama-cpp-python compilado para CPU)
# ---------------------------------------------------------------------------

FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm AS backend
# toolchain necessário para compilar llama-cpp-python (CPU)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /frontend/dist ./app/static

ENV DATA_DIR=/data \
    MODEL_PATH=/models/model.gguf \
    PYTHONUNBUFFERED=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
