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
    'broker_url': REDIS_DB_URL,
    'result_backend': REDIS_DB_URL,
    'result_expires': int(timedelta(hours=1).total_seconds()),
    'worker_redirect_stdouts_level': 'INFO',
    'worker_concurrency': 4,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json']
})
celery_app.conf.update(**vars(django.conf.settings._wrapped))
celery_app.autodiscover_tasks()
