# Dockerfile for Swordphish development instance
# written by CERT SG
#
# Must not be used directly, use docker-compose instead (see README.md)
#
# MAINTAINER CERT SG, cert.sg@socgen.com
FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-suggests --no-install-recommends \
    build-essential libpq-dev locales tzdata \
    python3-dev python3-pip python3-setuptools git && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/* /root/.cache/* && \
    groupadd swordphish && useradd -r --home-dir /opt/swordhish -g swordphish swordphish && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10 && \
    pip3 install --upgrade pip


ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/

COPY . /opt/swordphish

WORKDIR /opt/swordphish

# Setup locales
RUN locale-gen en_US.UTF-8 && \
        update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && \
        ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
        dpkg-reconfigure -f noninteractive tzdata && \
        LANG=en_US.UTF-8 pip install -r requirements.txt && \
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

RUN ./manage.py generate_secret_key

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["docker-entrypoint.sh", "webserver"]
