release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn kulfi_config.wsgi --log-file -
