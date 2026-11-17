#!/bin/sh
set -e

echo "Waiting for database..."
python <<'PY'
import os, time
import psycopg

dsn = (
    f"host={os.environ.get('POSTGRES_HOST', 'db')} "
    f"port={os.environ.get('POSTGRES_PORT', '5432')} "
    f"dbname={os.environ.get('POSTGRES_DB', 'inboxkit')} "
    f"user={os.environ.get('POSTGRES_USER', 'inboxkit')} "
    f"password={os.environ.get('POSTGRES_PASSWORD', 'inboxkit')}"
)

for attempt in range(60):
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"DB not ready ({attempt + 1}/60): {exc}")
        time.sleep(1)
else:
    raise SystemExit("Database never became ready.")
PY

echo "Waiting for Redis..."
python <<'PY'
import os, time
import redis

host = os.environ.get("REDIS_HOST", "redis")
port = int(os.environ.get("REDIS_PORT", "6379"))
client = redis.Redis(host=host, port=port)

for attempt in range(60):
    try:
        client.ping()
        print("Redis is ready.")
        break
    except Exception as exc:
        print(f"Redis not ready ({attempt + 1}/60): {exc}")
        time.sleep(1)
else:
    raise SystemExit("Redis never became ready.")
PY

python manage.py migrate --noinput
python manage.py ensure_board
python manage.py collectstatic --noinput

PORT="${PORT:-23000}"
exec daphne -b 0.0.0.0 -p "$PORT" config.asgi:application