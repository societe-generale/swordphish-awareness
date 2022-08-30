# Dockerfile for Swordphish development instance
# written by CERT SG
#
# Must not be used directly, use docker-compose instead (see README.md)
#
# MAINTAINER CERT SG, cert.sg@socgen.com
FROM python:3.10-slim

RUN apt update && apt upgrade -y && apt autoremove -y && \
    apt install git gcc libpq-dev python3-dev locales tzdata -y && pip3 install --upgrade pip

# Setup locales
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen && update-locale && \
    ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN groupadd swordphish && useradd -r --home-dir /opt/swordhish -g swordphish swordphish


ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/

COPY . /opt/swordphish

WORKDIR /opt/swordphish

RUN pip install -r requirements.txt && \
    cp Swordphish/settings.py Swordphish/settings_docker.py && \
    chown -R swordphish:swordphish /opt/swordphish && \
    sed -i '81s/FIXME/swordphish/' Swordphish/settings_docker.py && \
    sed -i '82s/FIXME/swordphish-postgres/' Swordphish/settings_docker.py && \
    sed -i '250s/localhost/swordphish-redis/' Swordphish/settings_docker.py && \
    sed -i '256s/hostname/localhost:8000/' Swordphish/settings_docker.py && \
    sed -i '256s/https/http/' Swordphish/settings_docker.py && \
    sed -i '306s/localhost/swordphish-mail/' Swordphish/settings_docker.py && \
    sed -i '307s/2525/1025/' Swordphish/settings_docker.py && \
    mv ./docker/scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh && \
    chmod 755 /usr/local/bin/wait-for-it.sh /usr/local/bin/docker-entrypoint.sh

USER swordphish
ENV HOME /opt/swordphish
ENV USER swordphish
ENV DJANGO_SETTINGS_MODULE Swordphish.settings_docker
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

RUN ./manage.py generate_secret_key

RUN ./manage.py collectstatic

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["webserver"]
