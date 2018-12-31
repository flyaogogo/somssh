#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: celery.py
# @Time: 18-4-17 下午4:42

from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somssh.settings')

app = Celery('somssh')

app.config_from_object('django.conf:settings')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def testTask():
    pass

