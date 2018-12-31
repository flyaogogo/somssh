# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from deploy.models import Project, SaltHost

from django.utils import timezone

# Create your models here.


class ProcessList(models.Model):
    project = models.ForeignKey(Project, verbose_name=u'所属项目')
    host = models.ForeignKey(SaltHost, verbose_name=u'部署主机')
    tag = models.CharField(max_length=30, unique=True, verbose_name=u'标签')
    process_user = models.CharField(max_length=80, blank=True, null=True, verbose_name=u'运行用户')
    process_pid = models.IntegerField(blank=True, null=True, verbose_name=u'PID')
    process_ppid = models.IntegerField(blank=True, null=True, verbose_name=u'PPID')
    process_cpu_per = models.FloatField(blank=True, null=True, verbose_name=u'CPU使用率')
    process_mem_per = models.FloatField(blank=True, null=True, verbose_name=u'内存使用率')
    process_rmem = models.IntegerField(blank=True, null=True, verbose_name=u'物理内存使用')
    process_start = models.CharField(max_length=80, blank=True, null=True, verbose_name=u'启动时间')
    process_etime = models.IntegerField(blank=True, null=True, verbose_name=u'运行时间')

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_process", u"查看进程"),
            ("edit_process", u"管理进程")
        )
        verbose_name = u'进程'
        verbose_name_plural = u'进程管理'


class ProcessMessage(models.Model):
    user = models.CharField(max_length=244, verbose_name=u'用户')
    project = models.CharField(max_length=80, verbose_name=u'项目名称')
    action = models.CharField(max_length=20, verbose_name=u'动作')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    content = models.TextField(verbose_name=u'详细日志')
    source_content = models.TextField(verbose_name=u'原始日志')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    class Meta:
        default_permissions = ()
        ordering = ['-id']
        verbose_name = u'进程管理日志'
        verbose_name_plural = u'进程管理日志管理'