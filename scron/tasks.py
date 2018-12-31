#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: tasks.py
# @Time: 18-4-24 下午6:25

from djcelery import models as celery_models
from django.utils import timezone
from somssh import celery_app

from deploy.models import Project
from sprocess.views import process_info
from lib.somssh_fun import net_info, get_sys_usage, get_disk_info
from lib.mongodb_api import GetSysData

import logging
import time

logger = logging.getLogger('django')


@celery_app.task()
def delete():
    '''
    删除任务
    从models中过滤出过期时间小于现在的时间然后删除
    '''
    return celery_models.PeriodicTask.objects.filter(expires__lt=timezone.now()).delete()


@celery_app.task()
def process_info_cron():
    projects = Project.objects.filter(status=True)

    for project in projects:
        logger.info("开始执行计划任务，获取进程信息")
        # 过滤禁用主机
        host_list = [i.ip for i in project.host_group.hosts.filter(status=True)]
        logger.info(u'主机： %s'%host_list)
        r = process_info(project, host_list)
        logger.info(u"结果：%s"%r)
        logger.info("项目{0}进程信息：{1}".format(project.name, r))


@celery_app.task()
def net_info_cron():
    logger.info("开始执行计划任务，获取SOMSSH服务器网络流量信息")
    r = net_info()
    logger.info("返回结果：{0}".format(r))
    db = GetSysData('network', 10, 'nettraffic')
    db.insert_data(r)
    return True


@celery_app.task()
def sys_usage_info():
    r = get_sys_usage()
    logger.info("获取系统资源使用: {}".format(r))
    return True


@celery_app.task()
def disk_info():
    #logger.info("获取磁盘信息： {}".format(get_disk_info()))
    return True

