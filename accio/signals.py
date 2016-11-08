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


def _delete_lru():
    from accio.models import Job
    lru_ids = Job.objects.order_by('-id')[celery_app.conf['ACCIO_JOBS_MAX_COUNT']:].values_list('id', flat=True)
    Job.objects.filter(pk__in=lru_ids).delete()


@before_task_publish.connect
def before_task_publish_handler(body, *options, **kwoptions):
    from accio.models import Job
    with transaction.atomic():
        _delete_lru()
        headers = kwoptions['headers']
        task_name = _simplify_task_name(headers['task'])
        task_id = headers['id']
        if not Job.objects.filter(task_id=task_id).exists():
            Job.objects.create(
                    task=_simplify_task_name(task_name),
                    args=headers['argsrepr'],
                    kwargs=headers['kwargsrepr'],
                    task_id=task_id,
                    state=states.PENDING,
                    category=headers['category'] or 'NONE',
                    scheduled=headers['scheduled']
            )


@task_prerun.connect
def prerun_handler(sender, task, task_id, args, kwargs, *options, **kwoptions):
    from accio.models import Job
    with transaction.atomic():
        try:
            job_Locked = Job.objects.select_for_update().get(task_id=task_id)
        except Job.DoesNotExist:
            raise ObjectDoesNotExist
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
