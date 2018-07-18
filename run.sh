# python manage.py migrate
# python manage.py collectstatic --no-input
gunicorn api.wsgi:application -b :80 --reload
