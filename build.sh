#!/usr/bin/env bash
# This runs during Render build time

echo "Running migrations and collectstatic..."
python manage.py migrate
python manage.py collectstatic --noinput
