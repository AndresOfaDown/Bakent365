web: python manage.py migrate && gunicorn mysmart.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --log-level debug
