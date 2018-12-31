#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: cron.py.py
# @Time: 17-12-26 下午6:32

from deploy.models import Project
from views import process_info

def process_info_cron():
    projects = Project.objects.filter(status=True)

    for project in projects:
        # 过滤禁用主机
        host_list = [i.ip for i in project.host_group.hosts.filter(status=True)]
        process_info(project, host_list)
