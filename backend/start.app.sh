#!/bin/bash

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    (python manage.py createsuperuser \
        --noinput \
        --email $DJANGO_SUPERUSER_EMAIL) || true
fi

python manage.py loaddata groups
python manage.py loaddata options
python manage.py loaddata month
python manage.py loaddata usergroups
# ── The version fixture is not optional ─────────────────────────────────────
# /api/v2/version/list serves this row to the frontend, which compares it
# against its own build-time version (frontend/package.json, stamped by the
# same release commit) and shows a "refresh to update" banner when they differ.
#
# This script has no `set -e`. So when `loaddata version` failed, it printed a
# traceback, execution carried on, gunicorn came up, and the database kept the
# PREVIOUS release's number -- which every client then compared against the NEW
# frontend and found different. The result is a refresh prompt that refreshing
# never clears, for every user, until someone reads the startup log.
#
# The container healthcheck cannot catch this: it curls /api/v2/version/list,
# which answers 200 with the stale row and looks perfectly healthy.
#
# Exiting is deliberate. A crash-loop is visible in `docker ps` within seconds;
# a silently stale version is not visible at all.
if ! python manage.py loaddata version; then
    echo "FATAL: could not load the version fixture." >&2
    echo "The database would keep the previous release's version number and" >&2
    echo "every client would be prompted to refresh forever. Refusing to start." >&2
    exit 1
fi
python manage.py scheduletasks
python manage.py loaddemodata

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
