#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: urls.py
# @Time: 18-1-5 上午11:32


from django.conf.urls import url
from views import *

urlpatterns = [
    # url(r'^$', index, name='index'),
    #url(r'job/index/$', job_index, name='job_index'),
    url(r'qcvm/list/$', qcvm_list, name='qcvm_list'),
    url(r'qcvm/import/$', qcvm_import, name='qcvm_import'),
    url(r'qlb/modify/$', qlb_modify, name='qlb_modify'),
    url(r'qcloud_loadbalancer/list/$', qlb_list, {'template_name': 'job_qlb_list.html'}, name='qlb_list'),
    url(r'qcloud_loadbalancer/manage/(?P<pid>\d+)/$', qlb_manage, name='qlb_manage'),
]