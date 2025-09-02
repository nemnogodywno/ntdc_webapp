#!/bin/sh
set -e

if [ -n "$DB_HOST" ]; then
  echo "Waiting for DB $DB_HOST:$DB_PORT..."
  for i in $(seq 1 40); do
    nc -z "$DB_HOST" "$DB_PORT" && break
    sleep 1
    if [ $i -eq 40 ]; then
      echo "Database not reachable" >&2
      exit 1
    fi
  done
fi

echo "Apply migrations"
python manage.py migrate --noinput

echo "Collect static"
python manage.py collectstatic --noinput || true

exec "$@"

