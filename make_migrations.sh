python3.11 admin_site/manage.py makemigrations
python3.11 admin_site/manage.py migrate
python3.11 admin_site/manage.py createsuperuser \
    --username=test \
    --email=test@example.com