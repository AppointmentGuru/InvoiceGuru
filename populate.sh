docker-compose run --rm db createdb appointmentguru_appointmentguru -h db -U postgres
docker-compose run --rm db createdb appointmentguru_medicalaidguru -h db -U postgres
docker-compose run --rm db createdb appointmentguru_invoiceguru -h db -U postgres

docker-compose run --rm appointmentguru python manage.py migrate
docker-compose run --rm medicalaidguru python manage.py migrate
docker-compose run --rm invoiceguru python manage.py migrate

docker-compose run --rm db psql -h db -U postgres -d appointmentguru_appointmentguru -W -f /code/appointmentguru.sql
docker-compose run --rm db psql -h db -U postgres -d appointmentguru_medicalaidguru -W -f /code/medicalaidguru.sql
docker-compose run --rm db psql -h db -U postgres -d appointmentguru_invoiceguru -W -f /code/invoiceguru.sql
