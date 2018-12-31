# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from deploy.models import SaltHost


# Create your models here.
class QcloudCVM(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=u'云主机')
    bid = models.CharField(max_length=100, unique=True, verbose_name=u'云主机ID')
    lanip = models.GenericIPAddressField(verbose_name=u'内网IP')
    wanip = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'外网IP')
    weight = models.IntegerField(default=10, verbose_name=u'权重')

    def __unicode__(self):
        return '%s-%s' % (self.name, self.bid)

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_qcvm", u"查看云主机"),
            ("edit_qcvm", u"管理云主机")
        )


class QcloudLB(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=u'负载均衡')
    lbid = models.CharField(max_length=100, unique=True, verbose_name=u'负载均衡ID')
    vip = models.GenericIPAddressField(verbose_name=u'负载均衡IP')
    region = models.CharField(max_length=20, verbose_name=u'区域')
    qcvm = models.ManyToManyField(QcloudCVM, related_name='qlb_qcvm_set', verbose_name=u'后端主机')
    # {0:创建中, 1:正常运行}
    status = models.IntegerField(default=1, verbose_name=u'运行状态')

    def __unicode__(self):
        return '%s-%s' % (self.name, self.lbid)

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_qlb", u"查看负载均衡"),
            ("edit_qlb", u"管理负载均衡")
        )
        verbose_name = u'负载均衡'
        verbose_name_plural = u'负载均衡管理'
