# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery.app import app_or_default
from celery.bin.beat import beat as Beat
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = 'Start celery beat'

    def handle(self, *args, **options):
        b = Beat(app_or_default())
        options = {
            'loglevel': 'INFO',
            'traceback': True
        }
        b.run(**options)
