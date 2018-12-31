#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: urls.py
# @Time: 18-3-28 下午2:28

from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'execute/nginx/$', nginx_modify, name='nginx_modify'),
    url(r'nginx_loadbalancer/list/$', nginx_list, {'template_name': 'job_nginx_list.html'}, name='nginx_list'),
    url(r'nginx_loadbalancer/manage/(?P<pid>\d+)/$', nginx_manage, name='nginx_manage'),
    url(r'nginx_loadbalancer/host/$', nginx_host, name='nginx_host'),
]
