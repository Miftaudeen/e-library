#!/bin/sh

python manage.py collectstatic --no-input --clear

python manage.py makemigrations --no-input

python manage.py migrate --no-input

python manage.py create_permisions --no-input

python manage.py create_superadmin --no-input

python manage.py runserver localhost:8000