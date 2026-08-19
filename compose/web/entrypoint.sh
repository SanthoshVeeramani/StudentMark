#!/usr/bin/env bash
set -e

# Wait for database to be available (basic)
echo "Waiting for database..."
MAX_RETRIES=30
RETRY=0
until python manage.py showmigrations >/dev/null 2>&1; do
  RETRY=$((RETRY+1))
  if [ $RETRY -gt $MAX_RETRIES ]; then
    echo "Database is not available after $MAX_RETRIES attempts, exiting."
    exit 1
  fi
  sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if env variables set (optional)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Creating superuser if not exists..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); email='$DJANGO_SUPERUSER_EMAIL'; pw='$DJANGO_SUPERUSER_PASSWORD'; uname='$DJANGO_SUPERUSER_USERNAME'; \
  u=User.objects.filter(email=email).first(); \
  \ 
  if not u: \ 
    User.objects.create_superuser(email, pw); \ 
    print('Superuser created.'); \ 
  else: \ 
    print('Superuser exists.');"
fi

echo "Starting Gunicorn..."
# Use 2 workers by default; tune for production
exec gunicorn student_portal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level info
