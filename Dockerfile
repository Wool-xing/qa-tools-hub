# Multi-stage build: frontend (Vue/Vite) + backend (FastAPI) → Uvicorn
# Build context: repository root
# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npx vite build --outDir /app/static --emptyOutDir

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/app/ ./app/
COPY backend/alembic.ini ./
COPY backend/migrations/ ./migrations/
COPY backend/pyproject.toml ./

# Copy built frontend from stage 1 into app/static/
COPY --from=frontend-build /app/static/ ./app/static/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8005/health')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
