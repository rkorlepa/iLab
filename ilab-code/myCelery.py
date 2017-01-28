#!/ws/rkorlepa-sjc/python/bin/python

from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('iLab',
             broker='pyamqp://ilab:nbv_12345@172.23.152.201//',
             include=['Utils'])

app.conf.update(
        result_expires=3600,
)

if __name__=='__main__':
    app.start()
