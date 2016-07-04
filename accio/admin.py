# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from celery.app import app_or_default
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from accio import models
from psutil import Process


@admin.register(models.Job)
class JobAdmin(ModelAdmin):
    list_display = ('task', 'args', 'kwargs', 'category',
                    'state', 'worker', 'elapsed_time', 'scheduled', 'timestamp_created')
    list_filter = ('state', 'category', 'scheduled', 'task')
    search_fields = ('task', 'args', 'kwargs', 'result')
    readonly_fields = ('timestamp_created', 'timestamp_modified', 'get_logs', 'elapsed_time',
                       'worker')
    fields = ('state', 'worker', 'task', 'task_id', 'category', 'args', 'kwargs', 'result',
              'scheduled', 'timestamp_created', 'timestamp_modified', 'elapsed_time', 'get_logs')

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        self.active_workers = app_or_default().control.inspect().active()
        return super(JobAdmin, self).changelist_view(request, extra_context=extra_context)

    def worker(self, obj):
        if self.active_workers:
            for node, active_workers in self.active_workers.iteritems():
                for worker in active_workers:
                    if worker['id'] == obj.task_id:
                        p = Process(worker['worker_pid'])
                        return 'CPU:%.1f%% RAM:%.2f%%' % (p.cpu_percent(0.05), p.memory_percent())
        return 'N/a'
