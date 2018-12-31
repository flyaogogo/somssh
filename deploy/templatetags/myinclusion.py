# -*- coding: utf8 -*-

from django import template
from django.db.models import Q

from deploy.models import *

register = template.Library()


@register.filter(name='host_user')
def host_user(arg):
    '''
    主机列表显示系统用户
    '''
    user_list = [i.username for i in arg.user.all()]
    return user_list

@register.filter(name='project_host')
def project_host(obj):
    #host_list = ['%s-%s' % (i.hostname, i.ip) for i in obj.all()]
    host_list = ['%s' % i.hostname for i in obj.all()]
    return host_list

@register.filter(name='job_host')
def job_host(obj, arg):
    try:
        # 过滤禁用主机
        host_list = JobBatch.objects.filter(jid=obj).get(tag=arg).host.all()
    except:
        host_list = None
    return host_list


def show_minions():
    '''
    远程命令、模块部署及文件上传中多项显示主机列表
    '''
    tgt_list = [i['hostname'] for i in SaltHost.objects.filter(status=True).values('hostname')]
    return {'tgt_list':sorted(list(set(tgt_list)))}

register.inclusion_tag('tag_minions.html')(show_minions)


