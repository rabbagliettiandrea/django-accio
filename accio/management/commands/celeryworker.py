# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery.app import app_or_default
from celery.bin.worker import worker as Worker
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Start celery worker'

    def handle(self, *args, **options):
        w = Worker(app_or_default())
        options = {
            'loglevel': 'DEBUG',
            'traceback': True
        }
        w.run(**options)
