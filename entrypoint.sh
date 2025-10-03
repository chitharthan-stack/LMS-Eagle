#!/usr/bin/env bash
set -e

# optional: short wait for DB (uncomment if DB sometimes needs a moment)
# echo "Waiting 5s for DB..."
# sleep 5

# Run migrations only if enabled in env (safer for production)
if [ "${RUN_MIGRATIONS_ON_START,,}" = "true" ] || [ "${RUN_MIGRATIONS_ON_START}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput || true
else
  echo "Skipping migrations (RUN_MIGRATIONS_ON_START not true)."
fi

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn lms_backend.wsgi:application --workers 3 --bind 0.0.0.0:8080 --log-level=info
    