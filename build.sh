#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt


python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate sites --noinput
python manage.py migrate --noinput
python manage.py showmigrations
python manage.py shell -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=2, defaults={'domain': 'awaafi.onrender.com', 'name': 'Awaafi'})"