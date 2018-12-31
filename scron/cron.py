#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: cron.py
# @Time: 18-1-19 下午2:07


from deploy.models import Project
from sprocess.views import process_info
from lib.somssh_fun import net_info, get_sys_info
from lib.mongodb_api import GetSysData

import time
import logging

logger = logging.getLogger('django')


def sys_info_cron():
    logger.info("开始执行计划任务，获取系统信息.")
    get_sys_info()


def net_info_cron():
    rlist = []
    for i in range(0, 11):
        logger.info("开始执行计划任务，获取SOMSSH服务器网络流量信息")
        r = net_info()
        rlist.append(r)
        t = 5
        logger.info("返回结果：{0}，休眠{1}秒".format(r, t))
        time.sleep(t)
    db = GetSysData('network', 10, 'nettraffic')
    db.multi_insert_data(rlist)



def process_info_cron():
    projects = Project.objects.filter(status=True)

    for project in projects:
        logger.info("开始执行计划任务，获取进程信息")
        # 过滤禁用主机
        host_list = [i.ip for i in project.host_group.hosts.filter(status=True)]
        r = process_info(project, host_list)
        logger.info("项目{0}进程信息：{1}".format(project.name, r))
