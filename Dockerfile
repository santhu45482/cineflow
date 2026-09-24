# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Stage 1: Build the React 19 Vite application
FROM node:24-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Unified Container with Python 3.12 FastAPI + Built React Assets
FROM python:3.12-slim

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

COPY ./pyproject.toml ./README.md ./uv.lock* ./
RUN uv sync --frozen

COPY ./app ./app
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port ${PORT:-8080}"]
