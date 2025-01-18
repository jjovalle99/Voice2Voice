# Base image
ARG BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Stage 1: Build the application
FROM ${BASE_IMAGE} AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Install dependencies without installing the project itself
RUN --mount=type=bind,source=../uv.lock,target=uv.lock \
    --mount=type=bind,source=../pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-cache --no-dev

# Add the entire application source code
ADD . /app

# Compile bytecode and sync dependencies for production
RUN touch README.md && uv sync --frozen --no-dev

# Stage 2: Prepare the runtime base image
FROM python:3.12-slim-bookworm AS runtime-base
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"

# Stage 3: Build the API service image
FROM runtime-base AS api
WORKDIR /app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]