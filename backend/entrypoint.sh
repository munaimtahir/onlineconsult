#!/bin/bash

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $POSTGRES_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist and seed data
echo "Seeding initial data..."
python manage.py seed_data

# Collect static files (for production)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Start server
echo "Starting server..."
if [ "$DJANGO_DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
