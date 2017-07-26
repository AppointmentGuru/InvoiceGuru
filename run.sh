python manage.py migrate
python manage.py collectstatic --no-input
gunicorn invoiceguru.wsgi:application -b :80 --reload
