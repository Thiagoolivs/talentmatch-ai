#!/bin/sh

echo "▶ Aguardando PostgreSQL..."

while ! nc -z $PGHOST $PGPORT; do
  echo "⏳ Banco não disponível em $PGHOST:$PGPORT. Tentando novamente..."
  sleep 2
done

echo "✔ Banco disponível!"

echo "▶ Rodando migrações..."
python manage.py migrate

echo "▶ Coletando estáticos..."
python manage.py collectstatic --noinput

echo "▶ Criando admin (idempotente)..."
python manage.py create_admin || true

echo "▶ Populando cursos e skills..."
python manage.py seed_courses || true
python manage.py seed_skills || true

echo "✔ Inicialização concluída. Subindo Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000
