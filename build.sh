#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt


python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate sites zero --noinput
python manage.py migrate sites --fake-initial --noinput
python manage.py migrate --noinput
python manage.py migrate --noinput
python manage.py showmigrations