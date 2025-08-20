FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system .

COPY app ./app
COPY alembic ./alembic
COPY frontend ./frontend
COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

USER appuser

EXPOSE 8000
CMD ["/entrypoint.sh"]