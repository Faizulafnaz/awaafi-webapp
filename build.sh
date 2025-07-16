#!/usr/bin/env bash
# exit on error
set -o errexit

set -o errexit

pip install psycopg2-binary
pip install dj-database-url
pip install -r requirements.txt



python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@gamil.com').exists() or User.objects.create_superuser( 'admin@gmail.com', 'admin@123')"
python manage.py showmigrations
