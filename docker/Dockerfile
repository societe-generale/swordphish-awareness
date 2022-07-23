# Dockerfile for Swordphish development instance
# written by CERT SG
#
# Must not be used directly, use docker-compose instead (see README.md)
#
# MAINTAINER CERT SG, cert.sg@socgen.com
FROM python:3.9-slim

RUN apt update && apt install git gcc libpq-dev python3-dev locales tzdata -y --no-install-suggests --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/* /root/.cache/* && \
    groupadd swordphish && useradd -r --home-dir /opt/swordhish -g swordphish swordphish

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/

RUN git clone https://github.com/certsocietegenerale/swordphish-awareness.git /opt/swordphish --depth=1 && rm -rf /opt/swordphish/.git

WORKDIR /opt/swordphish

# Setup locales
RUN locale-gen en_US.UTF-8 && \
        update-locale LANG=en_US.UTF-8 LC_ALL="en_US.UTF-8 UTF-8" && \
        ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
        dpkg-reconfigure -f noninteractive tzdata && \
        LANG=en_US.UTF-8 pip install -r requirements.txt && \
        cp Swordphish/settings.py Swordphish/settings_docker.py && \
        chown -R swordphish:swordphish /opt/swordphish && \
        sed -i '80s/FIXME/swordphish/' Swordphish/settings_docker.py && \
        sed -i '81s/FIXME/swordphish-postgres/' Swordphish/settings_docker.py && \
        sed -i '253s/localhost/swordphish-redis/' Swordphish/settings_docker.py && \
        sed -i '259s/hostname/localhost:8000/' Swordphish/settings_docker.py && \
        sed -i '259s/https/http/' Swordphish/settings_docker.py && \
        sed -i '309s/localhost/swordphish-mail/' Swordphish/settings_docker.py && \
        sed -i '310s/2525/1025/' Swordphish/settings_docker.py && \
        mv ./docker/scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh && \
        chmod 755 /usr/local/bin/wait-for-it.sh /usr/local/bin/docker-entrypoint.sh

USER swordphish
ENV HOME /opt/swordphish
ENV USER swordphish
ENV DJANGO_SETTINGS_MODULE Swordphish.settings_docker
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN ./manage.py generate_secret_key

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["docker-entrypoint.sh", "webserver"]
