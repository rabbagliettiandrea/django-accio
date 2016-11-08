# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery import Task
from django.db import transaction


class ManagedTask(Task):
    abstract = True  # Abstract classes are used as the base class for new task types.
    category = None
    force_run = True
    wait_secs = 0

    def apply(self, args=None, kwargs=None, link=None, link_error=None, **options):
        from accio import celery_app
        if not celery_app.conf['ACCIO_CELERY_ENABLED']:
            return
        return super(ManagedTask, self).apply(
                args=args, kwargs=kwargs, link=link, link_error=link_error, **options
        )

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None,
                    scheduled=False, countdown=wait_secs, **options):
        from accio import celery_app
        if not celery_app.conf['ACCIO_CELERY_ENABLED']:
            return
        return super(ManagedTask, self).apply_async(
            args, kwargs, task_id, producer, link, link_error,
            headers={'scheduled': scheduled, 'category': self.category},
            countdown=countdown, **options
        )

    def __call__(self, *args, **kwargs):
        if kwargs.pop('_force_run', self.force_run):
            from accio import celery_app
            if celery_app.conf['ACCIO_ATOMIC']:
                with transaction.atomic():
                    return super(ManagedTask, self).__call__(*args, **kwargs)
            else:
                return super(ManagedTask, self).__call__(*args, **kwargs)
        return 'Dry-Run due to condition'
