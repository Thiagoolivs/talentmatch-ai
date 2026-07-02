release: python manage.py migrate --noinput && python manage.py create_admin && python manage.py seed_courses && python manage.py seed_skills
web: python manage.py collectstatic --noinput && gunicorn talentmatch.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 60
