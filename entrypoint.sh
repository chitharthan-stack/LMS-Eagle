#!/usr/bin/env bash
set -e

if [ "${RUN_MIGRATIONS_ON_START,,}" = "true" ] || [ "${RUN_MIGRATIONS_ON_START}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput || true
else
  echo "Skipping migrations (RUN_MIGRATIONS_ON_START not true)."
fi

python manage.py collectstatic --noinput

exec gunicorn lms_backend.wsgi:application --workers 3 --bind 0.0.0.0:8080 --log-level=info
    