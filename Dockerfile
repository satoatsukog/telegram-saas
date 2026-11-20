FROM node:20-slim AS web
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=web /frontend/dist /app/frontend/dist
CMD ["/bin/sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
