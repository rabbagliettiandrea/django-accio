# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from celery import Celery
from accio.basetask import ManagedTask
import django.conf

default_app_config = 'accio.apps.Config'


REDIS_DB_URL = 'redis://127.0.0.1:6379/0'

celery_app = Celery(task_cls=ManagedTask)

celery_app.conf.update({
    # accio settings
    'ACCIO_CELERY_ENABLED': True,
    'ACCIO_ATOMIC': True,
    'ACCIO_LOGVAULT_URL': REDIS_DB_URL,
    'ACCIO_JOBS_MAX_COUNT': 1000,

    # celery settings
    'BROKER_URL': REDIS_DB_URL,
    'CELERY_RESULT_BACKEND': REDIS_DB_URL,
    'CELERY_TASK_RESULT_EXPIRES': int(timedelta(hours=1).total_seconds()),

    # Suggested celery settings
    'CELERYD_CONCURRENCY': 4,
    'CELERY_SEND_TASK_ERROR_EMAILS': True,
    'CELERY_TASK_SERIALIZER': 'msgpack',
    'CELERY_RESULT_SERIALIZER': 'msgpack',
    'CELERY_ACCEPT_CONTENT': ['msgpack']
})
celery_app.conf.update(**vars(django.conf.settings._wrapped))
celery_app.autodiscover_tasks()
