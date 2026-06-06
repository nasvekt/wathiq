# Wathiq — Production Dockerfile
# Build context: repo root (set Render Root Directory to ./, Dockerfile to backend/Dockerfile)
# Multi-stage: builds React frontend, serves everything from one container

FROM node:20 AS frontend-builder
WORKDIR /build/dashboard
COPY dashboard/package.json dashboard/package-lock.json* ./
RUN npm ci
COPY dashboard/ .
RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info fonts-noto-arabic fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend
COPY --from=frontend-builder /build/dashboard/dist/ /app/dashboard/dist/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]