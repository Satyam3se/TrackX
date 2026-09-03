#!/bin/sh
# ============================================================================
# TrackX — Web entrypoint
# Runs migrations + idempotent seed, then launches Daphne (ASGI).
# ============================================================================
set -e

echo "[entrypoint] Applying database migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Seeding initial data (idempotent)..."
python manage.py seed_trackx

echo "[entrypoint] Starting Daphne ASGI server on 0.0.0.0:8000..."
exec daphne -b 0.0.0.0 -p 8000 trackx.asgi:application
