#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: urls.py
# @Time: 17-12-25 下午5:37

from django.conf.urls import url
from views import *

urlpatterns = [
    # url(r'^$', index, name='index'),
    url(r'project/process/$', project_process, name='project_process'),
    url(r'project/process/manage/(?P<pid>\d+)/$', project_process_manage,
        {'template_name': 'project_process_manage.html'}, name='project_process_manage'),
    url(r'job/process/manage/(?P<pid>\d+)/$', project_process_manage, {'template_name': 'job_process_manage.html'},
        name='job_process_manage'),
    url(r'job/process/info/flush/(?P<pid>\d+)/$', process_info, name='process_flush'),
    url(r'job/process/log/tail/$', log_tail, name='log_tail'),
]
