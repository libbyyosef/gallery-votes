#!/usr/bin/env bash
set -euo pipefail

# Ensure DATABASE_URL is set; default to internal compose DB
: "${DATABASE_URL:=postgresql+psycopg://app:app@db:5432/app}"

echo "Waiting for DB…"
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text
url = os.environ["DATABASE_URL"]
engine = create_engine(url, future=True)
for i in range(60):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("DB is ready.")
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB did not become ready.")
PY

echo "Applying schema + seeding (idempotent)…"
python -m server.scripts.setup_db || true

echo "Starting API…"
exec uvicorn server.main:app --host 0.0.0.0 --port 8000
