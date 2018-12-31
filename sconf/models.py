#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: models.py.py
# @Time: 17-12-25 下午5:15

from __future__ import unicode_literals

from django.db import models
from deploy.models import Project
from django.utils import timezone
from django.contrib.auth.models import Permission


# Create your models here.

class ConfigList(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'文件名')
    tag = models.CharField(max_length=255, unique=True, default=timezone.now())
    project = models.ForeignKey(Project, verbose_name=u'所属项目')

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_config", u"查看配置文件"),
            ("edit_config", u"管理配置文件"),
        )
        ordering = ['-id']
        verbose_name = u'配置文件'
        verbose_name_plural = u'配置文件管理'


class ConfigBackup(models.Model):
    name = models.ForeignKey(ConfigList, verbose_name=u'文件名')
    path = models.CharField(max_length=255, verbose_name=u'备份路径')
    content = models.TextField(blank=True, null=True, verbose_name=u'返回内容')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')

    class Meta:
        default_permissions = ()
        ordering = ['-id']


class ConfigLog(models.Model):
    user = models.CharField(max_length=244, verbose_name=u'用户')
    project = models.CharField(max_length=80, verbose_name=u'项目名称')
    config = models.CharField(max_length=255, verbose_name=u'配置文件')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    content = models.TextField(verbose_name=u'详细日志')
    source_content = models.TextField(verbose_name=u'原始日志')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    # {False:发布日志, True:回退日志}
    msg_type = models.BooleanField(default=False, verbose_name=u'类型')

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_configlog", u"查看配置发布记录"),
            ("edit_configlog", u"管理配置发布记录"),
        )
        ordering = ['-id']
        verbose_name = u'配置发布记录'
        verbose_name_plural = u'配置发布记录管理'

