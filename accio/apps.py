# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'accio'
    verbose_name = 'django Accio'

    def ready(self):
        import accio.signals  # noqa
