#!/usr/bin/env sh

python -m venv django_venv      && \
sed -i 's/\r$//' django_venv/bin/activate && \
. django_venv/bin/activate && \
pip3 install -r requirements.txt && \
#sh

python3 manage.py migrate

python3 manage.py runserver
