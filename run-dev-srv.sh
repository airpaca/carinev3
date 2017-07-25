#!/bin/bash

cd /home/airpaca/carinev3
source .env/bin/activate
python manage.py runserver 0.0.0.0:5100


