#!/bin/sh

echo "▶ Aguardando PostgreSQL..."

while ! nc -z $PGHOST $PGPORT; do
  echo "⏳ Banco não disponível em $PGHOST:$PGPORT. Tentando novamente..."
  sleep 2
done

echo "✔ Banco disponível!"

echo "▶ Migrações..."
python manage.py migrate

echo "▶ Static..."
python manage.py collectstatic --noinput

echo "▶ Seeds..."
python manage.py create_admin || true
python manage.py seed_courses || true
python manage.py seed_skills || true

echo "✔ Iniciando Gunicorn..."
gunicorn talentmatch.wsgi:application --bind 0.0.0.0:8000

