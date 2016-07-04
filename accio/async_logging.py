# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import
import logging
from datetime import timedelta
from accio import celery_app
from redis import Redis


class RedisHandler(logging.Handler):
    def __init__(self, task_name, task_id, level):
        logging.Handler.__init__(self, level=level)
        self.redis_db = Redis.from_url(celery_app.conf['ACCIO_LOGVAULT_URL'])
        self.formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
        self.task_name = task_name
        self.task_id = task_id

    def emit(self, record):
        k = 'logs:%s:%s' % (self.task_name, self.task_id)
        self.redis_db.rpush(k, self.format(record))
        self.redis_db.expire(k, timedelta(weeks=1))


def getLogger(task_request):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if hasattr(task_request, 'task'):
        logger.addHandler(RedisHandler(task_request.task, task_request.id, level=logging.INFO))
    return logger
