# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery.app import app_or_default
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = 'Flush celery queue'

    def handle(self, *args, **options):
        n = app_or_default().control.purge()
        print '%d message(s) purged.\n' % n
