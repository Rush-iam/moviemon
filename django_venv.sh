#!/usr/bin/env sh

python -m venv django_venv      && \
sed -i 's/\r$//' django_venv/Scripts/activate && \
. django_venv/Scripts/activate && \
pip3 install -r requirements.txt && \
sh
