coverage run --branch --source=. ./manage.py test
coverage report
coverage xml
# python-codacy-coverage -r coverage.xml
