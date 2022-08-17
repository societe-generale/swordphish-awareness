# Docker support

This is probably the quickest way to test Swordphish.

## Install docker

Follow the [official instructions](https://www.docker.com/community-edition).

## Clone the repo

    $ git clone https://github.com/certsocietegenerale/swordphish-awareness
    $ cd swordphish-awareness

## Start Swordphish
The following command will build a Docker image named `swordphish` and launch it :

    $ cd docker
    $ docker-compose build
    $ docker-compose up

The `docker-compose up` command should start a working swordphish container listening for connections on `http://localhost:8000/`.

A fake smtp server and webmail is also available at `http://localhost:8025/` it allows to receive every mail sent by swordphish without the pain of setting up a full mail server.

But to be fully functional a few more commands need to be executed:

    $ docker exec swordphish_main ./manage.py loaddata docker/data_seed.json

This will inject a set of test data in the freshly instanciated database. You'll then be able to log with `admin@admin.com / password` on Swordphish.

Finally, if you want to fully test Swordphish campaigns, you should add the following line in your "hosts" file (/etc/hosts on most Unix / Linux systems and c:\Windows\System32\Drivers\etc\hosts on Windows).

    127.0.0.1 myphishingdomain.tld

## Notes

1. A custom configuration file can be mounted under Swordphish's image by editing the
compose file and using the `volumes` option. For example:
```
version: '3'
services:
  swordphish:
    container_name: swordphish_main
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    image: swordphish
    ports:
      - "8000:8000"
    links:
      - swordphish-redis
      - swordphish-postgres
      - swordphish-mail
    volumes:
      - /my/custom/swordphish/config:/opt/swordphish/Swordphish/settings_docker.py:ro
    restart: always
```
