python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py collectstatic --clear --no-input

gunicorn --pythonpath backend FIIT.wsgi:application --bind 0.0.0.0:8000 --workers 4 --reload
