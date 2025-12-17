# syntax=docker/dockerfile:1

# ---- Builder stage ----
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip wheel

COPY pyproject.toml ./
COPY apps ./apps
COPY packages ./packages

# Build wheels for the project and its dependencies
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

# ---- Final stage ----
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --ingroup app app

# Copy wheels from builder stage and install them
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels

USER app

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
