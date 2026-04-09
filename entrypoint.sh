#!/bin/bash
# Save this file with LF format instead of CRLF.
# If you are using VS Code you can easily do that at the bottom right corner of the window

# Collect static files
 echo "Collecting static files...."
 python manage.py collectstatic --noinput || exit 1

# Apply database migrations
echo "Apply database migrations"
#python manage.py makemigrations
#python manage.py makemigrations
python manage.py migrate

echo "Creating Translations"
python manage.py compilemessages

echo "Creating Superuser"
if [ -n "$SUPERUSER_USERNAME" ] && [ -n "$SUPERUSER_EMAIL" ] && [ -n "$SUPERUSER_PASSWORD" ]; then
	python manage.py init
else
	echo "Skipping superuser initialization (SUPERUSER_USERNAME/SUPERUSER_EMAIL/SUPERUSER_PASSWORD not fully set)."
fi

# Start server
echo "Starting server"

#gunicorn --preload core.wsgi:application --bind 0.0.0.0:8000 --timeout 600 --workers 3
#daphne --bind 0.0.0.0:8002 core.asgi:application
#daphne -b 0.0.0.0 -p 8000 core.asgi:application --root-path=/apiroute
daphne -b 0.0.0.0 -p 8000 core.asgi:application