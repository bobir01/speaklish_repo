#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done\

    echo "PostgreSQL started"
fi

# fill db with data

# python manage.py flush --no-input
python src/manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('bobir', '', 'bobdev2004')"



exec "$@"
