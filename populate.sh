docker-compose run --rm db psql -h db -U postgres -d appointmentguru_appointmentguru -W -f /code/appointmentguru.sql
docker-compose run --rm db psql -h db -U postgres -d appointmentguru_medicalaidguru -W -f /code/medicalaidguru.sql
docker-compose run --rm db psql -h db -U postgres -d appointmentguru_invoiceguru -W -f /code/invoiceguru.sql
