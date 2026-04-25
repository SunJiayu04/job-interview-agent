# Build frontend
FROM node:18 as builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install --legacy-peer-deps
COPY frontend ./frontend
RUN cd frontend && npm run build

# Backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY --from=builder /app/frontend/build /app/frontend_build

ENV PORT 8000
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
