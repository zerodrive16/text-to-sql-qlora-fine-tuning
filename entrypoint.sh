#!/bin/sh
set -e

echo "Applying database migrations..."
uv run manage.py migrate --noinput

echo "Collecting static files..."
uv run manage.py collectstatic --noinput

# Hand off to the container's main process (the CMD from the Dockerfile/compose)
exec "$@"
