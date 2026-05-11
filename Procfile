web: gunicorn styleai_project.wsgi:application --bind 0.0.0.0:$PORT
release: python -c "import django; django.setup(); print('Django OK')" && python manage.py migrate --verbosity=2