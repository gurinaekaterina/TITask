#!/usr/bin/env bash
set -euo pipefail

: "${ALEMBIC_DB_URL:?ALEMBIC_DB_URL is required}"

if [[ "${ALEMBIC_DB_URL}" == sqlite:* ]]; then
  DB_PATH="${ALEMBIC_DB_URL#sqlite:///}"
  if [[ "${DB_PATH}" != /* ]]; then
    DB_PATH="/app/${DB_PATH}"
  fi
  DB_DIR="$(dirname "${DB_PATH}")"
  mkdir -p "${DB_DIR}"
fi

alembic -c alembic/alembic.ini upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
