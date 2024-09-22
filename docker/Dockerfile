#FROM python:3.10-slim
FROM swordphish

RUN apt update && apt upgrade -y && apt autoremove -y && \
    apt install make git gcc libpq-dev python3-dev locales tzdata -y && pip3 install --upgrade pip

# Setup locales
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen && update-locale && \
    ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN groupadd swordphish && useradd -r --home-dir /opt/swordhish -g swordphish swordphish

WORKDIR /opt/swordphish
COPY requirements.txt /opt/swordphish/
RUN pip install -r requirements.txt

COPY . /opt/swordphish/

RUN mv ./docker/scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh && \
    chmod 755 /usr/local/bin/docker-entrypoint.sh

USER swordphish
ENV HOME /opt/swordphish
ENV USER swordphish
ENV DJANGO_SETTINGS_MODULE Swordphish.settings_docker
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

RUN ./manage.py generate_secret_key && ./manage.py collectstatic

EXPOSE 8000
