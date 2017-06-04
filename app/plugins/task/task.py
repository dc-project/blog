#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: task.py
@time: 2017/5/3 上午9:16
"""

from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name,backend=app.config['CELERY_RESULT_BACKEND'],broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        