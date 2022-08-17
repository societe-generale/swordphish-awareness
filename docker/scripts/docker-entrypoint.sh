#!/bin/bash
set -euo pipefail

function _wait_for_postgres {
      wait-for-it.sh swordphish-postgres:5432
}

function _wait_for_redis {
      wait-for-it.sh swordphish-redis:6379
}

if [ "$1" = 'webserver' ]; then
    _wait_for_postgres
    _wait_for_redis
    ./manage.py makemigrations && ./manage.py migrate
    exec ./manage.py runserver 0.0.0.0:8000
elif  [ "$1" = 'beat' ]; then
    _wait_for_postgres
    _wait_for_redis
    exec /usr/local/bin/celery -A Swordphish beat -l info
elif  [ "$1" = 'workers' ]; then
    _wait_for_postgres
    _wait_for_redis
    exec /usr/local/bin/celery -A Swordphish worker -l info
fi

exec "$@"
