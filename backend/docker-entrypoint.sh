#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! python3 -c "
import os, psycopg2
conn = psycopg2.connect(
    dbname=os.getenv('DATABASE_NAME'),
    user=os.getenv('DATABASE_USERNAME'),
    password=os.getenv('DATABASE_PASSWORD'),
    host=os.getenv('DATABASE_HOST'),
    port=os.getenv('DATABASE_PORT', 5432)
)
conn.close()
" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping 1s"
    sleep 1
done
echo "PostgreSQL is up!"

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Apply database migrations (DO NOT run makemigrations here!)
# Migrations should be created locally and committed to git
echo "Applying database migrations..."
python3 manage.py migrate --noinput

# Start server (Daphne for ASGI/WebSocket support)
echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 core.asgi:application
