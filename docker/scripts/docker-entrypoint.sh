
if [ "$1" = 'webserver' ]; then
    ./manage.py makemigrations && ./manage.py migrate
    export CONF=/opt/swordphish/config
    if [ ! -f "$CONF/.loaded" ]; then
      ./manage.py loaddata docker/data_seed.json && touch $CONF/.loaded
    fi
    exec ./manage.py runserver 0.0.0.0:8000
elif  [ "$1" = 'beat' ]; then
    exec /usr/local/bin/celery -A Swordphish beat -l info
elif  [ "$1" = 'workers' ]; then
    exec /usr/local/bin/celery -A Swordphish worker -l info
fi
