web: python manage.py collectstatic --noinput && gunicorn styleai_project.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate