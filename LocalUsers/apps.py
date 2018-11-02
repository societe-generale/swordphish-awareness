# -*- coding: utf-8 -*-
from django.apps import AppConfig


class LocalUsersConfig(AppConfig):
    name = "LocalUsers"

    def ready(self):
        from . import signals
