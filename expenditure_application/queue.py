# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from celery import Celery

queue = Celery(
    broker='amqp://guest@localhost',
    backend='amqp://guest@localhost',
    include=['expenditure_application.main'])
queue.conf.update(result_expires=3600)

if __name__ == '__main__':
    queue.start()
