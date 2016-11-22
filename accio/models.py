# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery import states
from django.db import models
from redis import Redis
import traceback
from accio import celery_app
from django.utils import timezone


class Job(models.Model):
    state = models.CharField(max_length=10, default=states.PENDING)
    task = models.CharField(max_length=256, db_index=True)
    task_id = models.UUIDField(unique=True, db_index=True)
    category = models.CharField(max_length=50)
    args = models.TextField(blank=True)
    kwargs = models.TextField(blank=True)
    result = models.TextField(blank=True)
    scheduled = models.BooleanField(default=False)
    timestamp_created = models.DateTimeField(auto_now_add=True, db_index=True, editable=False)
    timestamp_modified = models.DateTimeField(auto_now=True, db_index=True, editable=False)
    timestamp_prerun = models.DateTimeField(editable=False, null=True, blank=True)
    timestamp_postrun = models.DateTimeField(editable=False, null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def elapsed_time(self):
        if not self.timestamp_prerun and not self.timestamp_postrun:
            return 'N/a'
        secs = ((self.timestamp_postrun or timezone.now()) - self.timestamp_prerun).total_seconds()
        if secs < 60:
            return '%.1f sec(s)' % secs
        return '%d min(s), %.1f sec(s)' % (secs // 60, secs % 60)

    def __unicode__(self):
        return self.task

    def get_logs(self):
        try:
            redis_db = Redis.from_url(celery_app.conf['ACCIO_LOGVAULT_URL'], decode_responses=True)
            for result_k in redis_db.scan_iter('logs:*:%s' % self.task_id):
                logs = '\n'.join(line for line in redis_db.lrange(result_k, 0, -1))
                return '-- Logs will expire in: %s seconds --\n%s' % (redis_db.ttl(result_k), logs)
            return '-- Not available or expired --'
        except:
            return traceback.format_exc()
    get_logs.short_description = 'Logs'
