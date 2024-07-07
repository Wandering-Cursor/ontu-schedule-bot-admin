python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
uvicorn admin_site.asgi:application --host 0.0.0.0 --port 8000