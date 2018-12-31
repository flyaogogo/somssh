#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: models.py.py
# @Time: 17-6-19 上午11:09

from __future__ import unicode_literals

from django.db import models
# from django.contrib.auth.models import User
from userauth.models import User, UserGroup
from django.utils import timezone
from django.contrib.auth.models import Permission


# Create your models here.
def user_dir_path(instance, filename):
    if instance.visible == 0:
        return 'salt/module/user_{user_id}/{filename}'.format(user_id=instance.user.id, filename=filename)


def file_upload_dir_path(instance, filename):
    return 'salt/fileupload/user_{user_id}/{file_tag}/{filename}'.format(
        user_id=instance.user.id, file_tag=instance.file_tag, filename=filename)


class NetTraffic(models.Model):
    # somssh host network
    traffic = models.BigIntegerField(verbose_name=u'速率')
    # {0:in, 1:out}
    net_type = models.IntegerField(default=0, verbose_name=u'带宽类型')
    log_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    class Meta:
        default_permissions = ()
        ordering = ['-id']


class Region(models.Model):
    name = models.CharField(max_length=200, unique=True, default=u'广州二区', verbose_name=u'区域')
    region = models.CharField(max_length=250, unique=True, default='guangzhou2', verbose_name=u'区域简码')

    def __unicode__(self):
        return self.name

    class Meta:
        default_permissions = ()
        verbose_name = u'区域'
        verbose_name_plural = u'区域管理'


class SaltUser(models.Model):
    username = models.CharField(max_length=80, default='root', verbose_name=u'主机用户')
    password = models.CharField(max_length=255, default='123456', verbose_name=u'主机密码')
    tag = models.FloatField(default=0.0)

    def __unicode__(self):
        return self.username

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_user", u"查看主机用户"),
            ("edit_user", u"管理主机用户")
        )
        verbose_name = u'主机用户'
        verbose_name_plural = u'主机用户管理'


class SaltHost(models.Model):
    hostname = models.CharField(max_length=80, unique=True, verbose_name=u'主机名称')
    hostid = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'云主机ID')
    ip = models.GenericIPAddressField(verbose_name=u'主机IP')
    port = models.IntegerField(default=22, verbose_name=u'端口')
    user = models.ManyToManyField(SaltUser, related_name='user_set', verbose_name=u'主机用户')
    host_type = models.BooleanField(default=False, verbose_name=u'数据库主机')
    # status {True:启用, False:禁用}
    status = models.BooleanField(default=True, verbose_name=u'状态')
    # {0:IDC机房, 1:腾讯云, 2:阿里云}
    platform = models.IntegerField(default=0, verbose_name=u'平台')
    user_group = models.ManyToManyField(UserGroup, related_name='host_usergroup_set', verbose_name=u'主机属组')
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'所属区域')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')

    def __unicode__(self):
        return '%s' % (self.hostname)

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_host", u"查看主机"),
            ("edit_host", u"管理主机")
        )
        verbose_name = u'Salt主机'
        verbose_name_plural = u'Salt主机管理'


class SaltGroup(models.Model):
    groupname = models.CharField(
        max_length=80,
        unique=True,
        verbose_name=u'Salt主机组')
    user = models.CharField(max_length=80, default='zhifu_v35', verbose_name=u'部署用户')
    is_nginx = models.BooleanField(default=False, verbose_name=u'是否Nginx组')
    hosts = models.ManyToManyField(
        SaltHost,
        related_name='salt_host_set',
        verbose_name=u'Salt主机')
    user_group = models.ManyToManyField(UserGroup, related_name='group_usergroup_set', verbose_name=u'所属用户组')

    def __str__(self):
        return self.groupname

    class Meta:
        default_permissions = ()
        permissions = (
            ("edit_saltgroup", u"管理Salt主机分组"),
        )
        verbose_name = u'Salt主机分组'
        verbose_name_plural = u'Salt主机分组管理'


class Pcloud(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=u'项目名称')
    code = models.CharField(max_length=10, unique=True, verbose_name=u'项目简码')
    ip = models.ForeignKey(SaltHost, related_name='pcloud_ip', verbose_name=u'部署主机')
    user = models.ForeignKey(SaltUser, related_name='pcloud_user', verbose_name=u'部署用户')
    root_path = models.CharField(max_length=100, verbose_name=u'ROOT路径')
    service_path = models.CharField(max_length=100, verbose_name=u'Service路径')
    db_host = models.ForeignKey(SaltHost, related_name='pcloud_dbhost', verbose_name=u'数据库主机')
    db_user = models.ForeignKey(SaltUser, related_name='pcloud_dbuser', verbose_name=u'数据库用户')
    sid = models.CharField(max_length=10, verbose_name=u'SID')
    memcached = models.CharField(max_length=255, verbose_name=u'Memcached')
    status = models.BooleanField(default=True, verbose_name=u'启用')
    publish_status = models.BooleanField(default=False, verbose_name=u'发布状态')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')

    def __unicode__(self):
        return '%s-%s' % (self.name, self.code)

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_pcloud", u"查看私有云"),
            ("edit_pcloud", u"管理私有云"),
            ("delete_pcloud", u"删除私有云")
        )
        verbose_name = u'私有云'
        verbose_name_plural = u'私有云管理'


class Project(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=u'项目名称')
    host_group = models.ForeignKey(SaltGroup, blank=True, null=True, verbose_name=u'部署主机组', on_delete=models.SET_NULL)
    path = models.CharField(max_length=100, verbose_name=u'项目路径')
    code_path = models.CharField(max_length=255, default=None, verbose_name=u'SVN路径')
    code_user = models.CharField(max_length=80, blank=True, null=True, verbose_name=u'SVN用户')
    code_passwd = models.CharField(max_length=80, blank=True, null=True, verbose_name=u'SVN密码')
    port = models.IntegerField(default=9000, verbose_name=u'服务端口')
    war = models.CharField(max_length=100, default='ROOT', verbose_name=u'全量包名')
    version = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'当前版本')
    user_group = models.ManyToManyField(UserGroup, related_name='project_usergroup_set', verbose_name=u'项目属组')
    lb_nginx = models.ManyToManyField(SaltGroup, related_name='nginx_hostgroup_set', verbose_name=u'Nginx负载', blank=True)
    lb_vip = models.GenericIPAddressField(blank=True, null=True, verbose_name=u'负载均衡VIP')
    lb_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'负载均衡ID')
    # {0:tomcat, 1:play}
    container = models.IntegerField(default=0, verbose_name=u'容器')
    status = models.BooleanField(default=True, verbose_name=u'启用')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    def __unicode__(self):
        return self.name

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_project", u"查看项目"),
            ("edit_project", u'管理项目'),
            ("delete_project", u'删除项目')
        )
        ordering = ['-modify_time']
        verbose_name = u'项目'
        verbose_name_plural = u'项目管理'


FILE_TYPE = (
    (0, u'全量备份'),
    (1, u'增量备份'),
    (2, u'配置备份')
)


class ProjectBackup(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255, verbose_name=u'文件名')
    file_type = models.IntegerField(default=0, choices=FILE_TYPE, verbose_name=u'文件类型')
    path = models.CharField(max_length=255, verbose_name=u'备份路径')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')

    class Meta:
        default_permissions = ()


class Job(models.Model):
    jid = models.CharField(max_length=255, unique=True, verbose_name=u'任务ID')
    user = models.ForeignKey(User, verbose_name=u'创建人')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    # tag = models.CharField(max_length=255, verbose_name=u'发布批次')
    project = models.ForeignKey(Project, related_name='job_project_set', verbose_name=u'项目')
    # {0:全量, 1:增量, 2:配置文件}
    pub_type = models.IntegerField(default=0, verbose_name=u'发布类型')
    source = models.IntegerField(default=0, verbose_name=u'文件来源')
    pub_path = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'发布路径')
    version = models.CharField(max_length=100, verbose_name=u'发布版本')
    ifreload = models.IntegerField(default=0, verbose_name=u'进程管理')
    last_step = models.IntegerField(default=0, verbose_name=u'最近发布批次')
    # {0:未结单，1:已结单，2:已作废}
    status = models.IntegerField(default=0, verbose_name=u'任务状态')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    remark = models.TextField(blank=True, null=True, verbose_name=u'备注')

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_job', u'查看发布任务'),
            ('edit_job', u'管理发布任务'),
            ('delete_job', u'删除发布任务')
        )
        ordering = ['-modify_time']
        verbose_name = u'发布任务'
        verbose_name_plural = u'发布任务管理'


class JobBatch(models.Model):
    jid = models.ForeignKey(Job, blank=True, null=True, on_delete=models.SET_NULL)
    jtag = models.CharField(max_length=255, unique=True, verbose_name=u'标签')
    tag = models.CharField(max_length=100, verbose_name=u'发布批次')
    host = models.ManyToManyField(SaltHost, verbose_name=u'发布主机')
    path = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'备份路径')
    # {0:未发布, 1:已发布, 2:已回退}
    # 0： 可发布，不可回退
    # 1： 可回退
    # 2： 不可回退
    status = models.IntegerField(default=0, verbose_name=u'发布状态')

    class Meta:
        default_permissions = ()
        permissions = (
            ('exec_job', u'版本发布'),
        )


class JobLock(models.Model):
    # 任务发布锁
    job = models.OneToOneField(Job)

    class Meta:
        default_permissions = ()


class JobTmpl(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True)
    jtag = models.CharField(max_length=255, unique=True, verbose_name=u'标签')
    tag = models.CharField(max_length=100, verbose_name=u'发布批次')
    host = models.ManyToManyField(SaltHost, verbose_name=u'发布主机')

    class Meta:
        default_permissions = ()


class JobLog(models.Model):
    jid = models.ForeignKey(Job, blank=True, null=True, verbose_name=u'任务ID')
    user = models.ForeignKey(User, verbose_name=u'执行人')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    batch = models.ForeignKey(JobBatch, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'发布批次')
    btag = models.CharField(max_length=255, unique=True, verbose_name=u'标签')
    version_history = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'回退版本')
    version_path = models.CharField(max_length=100, verbose_name=u'备份路径')
    content = models.TextField(verbose_name=u'详细日志')
    source_content = models.TextField(verbose_name=u'原始日志')
    # {True:已回退, False:未回退}
    status = models.BooleanField(default=False, verbose_name=u'回退状态')
    pub_status = models.BooleanField(default=False, verbose_name=u'发布状态')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_joblog', u'查看发布日志'),
            ('edit_joblog', u'管理发布日志')
        )
        ordering = ['-created_time']
        verbose_name = u'发布日志'
        verbose_name_plural = u'发布日志管理'


class JobRollbackLog(models.Model):
    jid = models.ForeignKey(Job, blank=True, null=True, verbose_name=u'任务ID')
    jlog = models.ForeignKey(JobLog, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'发布日志')
    user = models.ForeignKey(User, verbose_name=u'执行人')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    content = models.TextField(verbose_name=u'详细日志')
    source_content = models.TextField(verbose_name=u'原始日志')
    # {True:回退成功, False:回退失败}
    status = models.BooleanField(default=False, verbose_name=u'回退状态')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')

    class Meta:
        default_permissions = ()
        ordering = ['-created_time']
        verbose_name = u'回退日志'
        verbose_name_plural = u'回退日志管理'


class Message(models.Model):
    user = models.CharField(max_length=244, verbose_name=u'用户')
    audit_time = models.DateTimeField(auto_now_add=True, verbose_name=u'时间')
    type = models.CharField(max_length=10, verbose_name=u'类型')
    action = models.CharField(max_length=20, verbose_name=u'动作')
    action_ip = models.CharField(max_length=15, verbose_name=u'来源IP')
    content = models.TextField(verbose_name=u'内容')

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_message", u"查看日志审计"),
            ("edit_message", u"管理日志审计"),
        )
        ordering = ['-audit_time']
        verbose_name = u'审计信息'
        verbose_name_plural = u'审计信息管理'


class JobMessage(models.Model):
    user = models.CharField(max_length=244, verbose_name=u'用户')
    project = models.CharField(max_length=80, verbose_name=u'项目名称')
    jid = models.CharField(max_length=255, verbose_name=u'任务ID')
    action_ip = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'来源IP')
    batch = models.CharField(max_length=100, verbose_name=u'发布批次')
    content = models.TextField(verbose_name=u'详细日志')
    source_content = models.TextField(verbose_name=u'原始日志')
    ## {True:已回退, False:未回退}
    # {True: 成功, False： 失败}
    status = models.BooleanField(default=False, verbose_name=u'状态')
    created_time = models.DateTimeField(default=timezone.now, verbose_name=u'创建时间')
    # {False:发布日志, True:回退日志}
    msg_type = models.BooleanField(default=False, verbose_name=u'类型')

    class Meta:
        default_permissions = ()
        ordering = ['-id']
        verbose_name = u'发布信息'
        verbose_name_plural = u'发布信息管理'
