#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: urls.py
# @Time: 17-6-19 上午11:03

from django.conf.urls import url
from views import *

urlpatterns = [
    # url(r'^$', index, name='index'),
    url(r'job/index/$', job_index, name='job_index'),
    url(r'host/region/list/$', region_list, name='region_list'),
    url(r'host/region/add/$', region_manage, name='region_add'),
    url(r'host/region/(?P<id>\d+)/(?P<action>[\w-]+)/$', region_manage, name='region_manage'),
    url(r'host/user/list/$', saltuser_list, name='saltuser_list'),
    url(r'host/user/add/$', saltuser_manage, name='saltuser_add'),
    url(r'host/user/(?P<id>\d+)/(?P<action>[\w-]+)/$', saltuser_manage, name='saltuser_manage'),
    url(r'host/list/$', salthost_list, name='salthost_list'),
    url(r'host/manage/add/$', salthost_manage, name='salthost_add'),
    url(r'host/manage/(?P<id>\d+)/(?P<action>[\w-]+)/$', salthost_manage, name='salthost_manage'),
    url(r'host/manage/system_user/update/$', salthost_user_update, name='update_user'),
    url(r'host/manage/system_user/delete/$', salthost_user_delete, name='delete_user'),
    url(r'host/group/list/$', saltgroup_list, name='saltgroup_list'),
    url(r'host/group/manage/add/$', saltgroup_manage, name='saltgroup_add'),
    url(r'host/group/manage/(?P<id>\d+)/(?P<action>[\w-]+)/$', saltgroup_manage, name='saltgroup_manage'),
    url(r'project/list/$', project_list, name='project_list'),
    url(r'project/manage/add/$', project_manage, name='project_add'),
    url(r'project/manage/(?P<id>\d+)/(?P<action>[\w-]+)/$', project_manage, name='project_manage'),
    url(r'project/manage/host/user/$', ajax_hostuser, name='ajax_hostuser'),
    url(r'project/release/host/(?P<pid>\d+)/$', ajax_host, name='ajax_host'),
    url(r'project/release/get_host/$', get_host, name='get_host'),
    url(r'log/audit/action/$', log_action, name='log_action'),
    url(r'log/audit/login/$', log_login, name='log_login'),
    url(r'file/upload/$', salt_file_upload, name='salt_file_upload'),
    url(r'job/list/$', job_list, name='job_list'),
    url(r'job/list/(?P<pid>\d+)/$', job_list, name='job_list'),
    url(r'job/list/ajax/$', job_ajax, name='job_ajax'),
    url(r'job/template/(?P<pid>\d+)/(?P<action>[\w-]+)/$', job_tmpl, name='job_manage_tmpl'),
    url(r'job/quick_create/$', job_manage_quick, name='job_create_quick'),
    url(r'job/(?P<pid>\d+)/(?P<action>[\w-]+)/$', job_manage, name='job_create'),
    url(r'job/edit/(?P<pid>\d+)/(?P<jid>\d+)/(?P<action>[\w-]+)/$', job_manage, name='job_edit'),
    url(r'job/cancle/(?P<pid>\d+)/(?P<jid>\d+)/$', job_cancle, name='job_cancle'),
    url(r'job/execute/(?P<pid>\d+)/(?P<jid>\d+)/$', job_exec, name='job_exec'),
    url(r'job/rollback/(?P<pid>\d+)/(?P<jid>\d+)/$', job_rollback, name='job_rollback'),
    url(r'job/execute/(?P<pid>\d+)/(?P<jid>\d+)/step/status/$', job_step_status, name='job_step_status'),
    url(r'job/execute/(?P<pid>\d+)/(?P<jid>\d+)/step=(?P<step>\d+)/$', job_exec_step, name='job_exec_step'),
    url(r'job/history/ajax/$', joblog_ajax, name='joblog_ajax'),
    url(r'job/history/$', job_history, name='job_history'),
    url(r'job/history/(?P<jid>\d+)/$', job_history, name='job_history'),
    url(r'job/history/release/detail/$', job_history_detail, name='job_history_detail'),
    url(r'job/history/rollback/detail/$', job_rollback_detail, name='job_rollback_detail'),
    url(r'job/history/host/$', job_host, name='job_ajax_host'),
    url(r'job/help/$', job_help, name='job_help'),
    url(r'salt/filemanage/host/$', ajax_host, name='ajax_host_upload'),
]
