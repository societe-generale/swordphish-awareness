# Docker support

This is probably the quickest way to test Swordphish.

## Install docker

Follow the [official instructions](https://www.docker.com/community-edition).

## Clone the repo

```bash
    $ git clone https://github.com/societe-generale/swordphish-awareness
    $ cd swordphish-awareness
```

## Start Swordphish

The following command will build a Docker image named `swordphish` and launch it :

```bash
    $ cd docker
    $ docker-compose up
```

The `docker-compose up` command should start a working swordphish container listening for connections
on `http://localhost:8000/`.

### Test the application

- Go to http://localhost:8000/
- Login with `admin@admin.com` and `password` credentials
- Duplicate existing campaign and test

A fake smtp server and webmail is also available at `http://localhost:8025/` it allows to receive every mail sent by
swordphish without the pain of setting up a full mail server.

You can add local DNS records in your "hosts" file (
/etc/hosts on most Unix / Linux systems and C:\Windows\System32\Drivers\etc\hosts on Windows)
to use other phishmail domains:

```
    127.0.0.1 global.corp
    127.0.0.1 myphishingdomain.tld
    ...
```

## Notes

1. A custom configuration file can be mounted under Swordphish's image by editing the
   compose file and using the `volumes` option. For example:

```yaml
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
