# syntax=docker/dockerfile:1

# ---------- Base Stage ----------
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
# ignore 'Running pip as the root user...' warning
ENV PIP_ROOT_USER_ACTION=ignore
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*
# Update pip
RUN pip install --no-cache-dir --upgrade pip

# ---------- Build Stage ----------
FROM base AS build
ENV POETRY_VERSION=2.1.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \ 
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/src/.cache/pypoetry
# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /src
# Copy the lock file and pyproject.toml first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./
# Install production dependencies
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} \
    poetry install --without test,dev --no-root
# Copy the rest of the application code
COPY . .

# ---------- Test Stage ----------
# This stage is used for running tests
FROM build AS test
WORKDIR /src
ENV PATH="/src/.venv/bin:$PATH"
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} \
    poetry install --without dev
CMD ["poetry", "run", "pytest" ]

# ---------- Development Stage ----------
FROM build AS dev
WORKDIR /src
ENV PATH="/src/.venv/bin:$PATH" DEBUG=1 ENVIRONMENT=development
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} poetry install
CMD ["uvicorn", "app.main:app" ,"--host", "0.0.0.0", "--port", "8000"]

# ---------- Runtime Stage ----------
# This stage is used for production deployments
FROM base AS runtime
ENV VIRTUAL_ENV=/src/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

WORKDIR /src
COPY --from=build /src/.venv ${VIRTUAL_ENV}
COPY --from=build /src/app ./app

# Creates a non-root user with an explicit UID and adds permission to access the /src folder
RUN adduser -u 56781 --disabled-password --gecos "" appuser && chown -R appuser /src
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
