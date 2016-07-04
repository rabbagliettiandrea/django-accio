# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from celery import states
from celery.signals import task_prerun, task_postrun, task_success, task_failure, before_task_publish
from accio import celery_app
from django.core.exceptions import ObjectDoesNotExist
from kombu.utils.encoding import safe_repr
from django.db import transaction
from django.utils import timezone


def _simplify_task_name(task_name):
    return '.'.join(task_name.split('.')[-3:])


@before_task_publish.connect
def before_task_publish_handler(body, *options, **kwoptions):
    from accio.models import Job
    with transaction.atomic():
        Job.objects.order_by('-id')[celery_app.conf['ACCIO_JOBS_MAX_COUNT']:].delete()  # don't let Job model explodes
        task_name = _simplify_task_name(body['task'])
        headers = kwoptions['headers']
        task_id = body['id']
        if not Job.objects.filter(task_id=task_id).exists():
            Job.objects.create(
                    task=task_name,
                    args=safe_repr(body['args']),
                    kwargs=safe_repr(body['kwargs']),
                    task_id=task_id,
                    state=states.PENDING,
                    category=headers['category'] or 'MISC',
                    scheduled=headers['scheduled']
            )


@task_prerun.connect
def prerun_handler(sender, task, task_id, args, kwargs, *options, **kwoptions):
    from accio.models import Job
    with transaction.atomic():
        job_Locked, created = Job.objects.select_for_update().get_or_create(task_id=task_id, defaults={
            'task': _simplify_task_name(task.name),
            'args': safe_repr(args),
            'kwargs': safe_repr(kwargs),
            'category': task.category
        })
        job_Locked.state = states.STARTED
        job_Locked.timestamp_prerun = timezone.now()
        job_Locked.save()


@task_postrun.connect
def postrun_handler(sender, task, task_id, signal, state, retval, *args, **kwargs):
    from accio.models import Job
    with transaction.atomic():
        try:
            job_Locked = Job.objects.select_for_update().get(task_id=task_id)
        except Job.DoesNotExist:
            raise ObjectDoesNotExist
        job_Locked.state = state or 'UNKNOWN'
        job_Locked.timestamp_postrun = timezone.now()
        job_Locked.save()


@task_success.connect
def success_handler(sender, result, *args, **kwargs):
    from accio.models import Job
    with transaction.atomic():
        try:
            job_Locked = Job.objects.select_for_update().get(task_id=sender.request.id)
        except Job.DoesNotExist:
            raise ObjectDoesNotExist
        job_Locked.result = safe_repr(result) or ''
        job_Locked.save()


@task_failure.connect
def failure_handler(sender, task_id, exception, traceback, einfo, *args, **kwargs):
    from accio.models import Job
    with transaction.atomic():
        try:
            job_Locked = Job.objects.select_for_update().get(task_id=task_id)
        except Job.DoesNotExist:
            raise ObjectDoesNotExist
        job_Locked.result = einfo.traceback
        job_Locked.save()
