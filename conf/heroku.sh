#!/bin/bash
python manage.py migrate
python manage.py loaddata 000_site_dev
python manage.py loaddata 000_admin
python manage.py loaddata 001_pin
python manage.py collectstatic --noinput
