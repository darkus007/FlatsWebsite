#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo ">>>> Waiting for postgres... <<<<"

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo ">>>> PostgreSQL started <<<<"
fi

python manage.py makemigrations
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

exec "$@"