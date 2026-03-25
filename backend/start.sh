#!/bin/bash

# apply migrations
echo "Applying migrations..."
python manage.py migrate

# create superuser
echo "Creating superuser :)..."
python manage.py seed_superuser

# start the server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000