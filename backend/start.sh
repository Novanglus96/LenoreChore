#!/bin/bash

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
#python manage.py createcachetable

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    (python manage.py createsuperuser \
        --noinput \
        --email $DJANGO_SUPERUSER_EMAIL) ||
        true
fi

python manage.py loaddata groups
python manage.py loaddata options
python manage.py loaddata month
python manage.py loaddata usergroups
#python manage.py loaddata admin_interface_theme_lenorechore

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
