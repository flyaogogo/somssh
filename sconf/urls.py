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
    url(r'project/get_config/$', get_config, name='get_config'),
    url(r'job/project/config/(?P<pid>\d+)/$', project_config, {'template_name':'job_project_config.html'}, name='project_config'),
    url(r'job/project/config/(?P<pid>\d+)/check/$', project_config_check, name='project_config_check'),
    url(r'job/project/config/(?P<pid>\d+)/rollback$', project_config, {'template_name':'job_project_config_rollback.html'}, name='project_config_rollback'),
    url(r'job/project/config/history/$', get_config_version, name='ajax_config'),
    url(r'^salt/push_config/$', push_config, name='push_config'),
]
