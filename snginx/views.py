#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: views.py
# @Time: 17-6-19 上午11:10

from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from deploy.models import Project, Message, SaltGroup
from userauth.views import username_auth, user_ip

from salt.client.ssh.client import SSHClient
import time
import json

# Create your views here.

import logging

logger = logging.getLogger(__name__)  # 这里用__name__通用,自动检测.
# Create your views here.


def job_exec_nginx(host_list, dest_file, bid_list, port, sls, roster_file, desc):
    c = SSHClient()
    data = {'dest_file': dest_file, 'backends': bid_list, 'port': port}
    result_source = c.cmd(tgt=host_list, fun='state.sls', roster_file=roster_file,
                          arg=[sls, 'pillar=%s' % json.dumps(data)], expr_form='list')
    result = []
    keys = result_source.keys()
    keys.sort()
    for i in keys:
        value = result_source[i]
        t_upstream = {}
        t_reload = {}
        ret = 0
        if value['retcode'] != 0:
            ret = 103
        for k, v in value['return'].items():
            keys = k.split('|')
            if keys[-1] == '-replace':
                t_upstream[keys[1]] = {'comment': v['comment'], 'result': v['result']}
            if keys[1] == '-nginx-reload_':
                if v['changes']:
                    if v['changes']['retcode'] != 0:
                        ret = 102 # test failed
                    t_reload = {'comment': v['comment'], 'result': v['result'], 'retcode': v['changes']['retcode'], 'stderr': v['changes']['stderr']}
                else:
                    t_reload = {'comment': v['comment'], 'result': v['result']}
                if v['comment'] == 'onlyif execution failed':
                    ret = 99

        r = {'host': i, 'backends': t_upstream, 'reload': t_reload, 'retcode': value['retcode'], 'ret': ret}
        result.append(r)

        if value['retcode'] == 0 and ret == 0:
            temp = '成功'
        elif ret == 99:
            temp = '失败：配置无任何变更'
        elif ret == 102:
            temp = '失败：配置测试不通过'
        else:
            temp = '失败：未知异常'
        logger.info('{0}nginx服务器{1}后端{2}:{3}{4}，返回信息：{5}'.format(desc, i, bid_list, port, temp, r))

    return {'result': result, 'source': result_source}


@login_required
#@permission_required('qcloud.view_qlb')
def nginx_modify(request):
    retcode = 0
    if request.is_ajax():
        if not request.user.has_perms(['qcloud.edit_qlb']):
            return JsonResponse({'retcode': 101})
        pid = request.POST.get('project')
        nginx_group = request.POST.get('nginx_group')
        project = Project.objects.get(pk=pid)
        if not project.status:
            return JsonResponse({'retcode': 100})
        nginx = SaltGroup.objects.get(pk=nginx_group)
        bid_list = request.POST.getlist('bid_list[]')
        action = request.POST.get('action')

        # 过滤禁用的主机
        nginx_hosts = [i.ip for i in nginx.hosts.filter(status=True)]
        roster_file = './media/salt/project_roster/roster_hostgroup_%s' % (nginx_group)
        dest_file = '/opt/nginx/conf/upstream.conf'
        ret = []

        if action == 'del':
            ## 摘除后端
            sls = 'job_exec_nginx_comment'
            desc = '摘除'
            r = job_exec_nginx(nginx_hosts, dest_file, bid_list, project.port, sls, roster_file, desc)
            logger.info("开始{}Nginx后端".format(desc))
            logger.info(
                "函数：job_exec_nginx，参数：nginx_hosts={0}, dest_file={1}, bid_list={2}, project.port={3}, sls={4}, roster_file={5}".format(
                    nginx_hosts, dest_file, bid_list, project.port,
                    sls, roster_file))
        else:
            ## 挂载后端
            r = {'source': {}, 'result': []}
            sls = 'job_exec_nginx_uncomment'
            desc = '挂载'
            logger.info("开始{}Nginx后端".format(desc))
            ## 循环挂载nginx后端，避免由于量大导致部分请求超时（服务处理不过来, 瞬间资源飙高）
            # for host in nginx_hosts:
            #     logger.info(
            #         "函数：job_exec_nginx，参数：nginx_hosts={0}, dest_file={1}, bid_list={2}, project.port={3}, sls={4}, roster_file={5}".format(
            #             host, dest_file, bid_list, project.port,
            #             sls, roster_file))
            #     t = job_exec_nginx(host, dest_file, bid_list, project.port, sls, roster_file, desc)
            #     r['source'] = dict(r['source'], **t['source'])
            #     #r['result'] = dict(r['result'], **t['result'])
            #     r['result'].extend(t['result'])
            #     logger.info("{}后端{}，结果：{}.".format(desc, host, t))

            ## 金字塔循环挂载nginx后端，避免由于量大导致部分请求超时（服务处理不过来, 瞬间资源飙高）
            p = 0
            while(len(nginx_hosts)):
                p += 1
                if p < len(nginx_hosts) / 2:
                    logger.info(
                        "函数：job_exec_nginx，参数：nginx_hosts={0}, dest_file={1}, bid_list={2}, project.port={3}, sls={4}, roster_file={5}".format(
                            nginx_hosts[0:p], dest_file, bid_list, project.port,
                            sls, roster_file))
                    t = job_exec_nginx(nginx_hosts[0:p], dest_file, bid_list, project.port, sls, roster_file, desc)
                    r['source'] = dict(r['source'], **t['source'])
                    r['result'].extend(t['result'])
                    logger.info("{}后端{}，结果：{}.".format(desc, nginx_hosts[0:p], t))
                    del nginx_hosts[0:p]
                else:
                    logger.info(
                        "函数：job_exec_nginx，参数：nginx_hosts={0}, dest_file={1}, bid_list={2}, project.port={3}, sls={4}, roster_file={5}".format(
                            nginx_hosts, dest_file, bid_list, project.port,
                            sls, roster_file))
                    t = job_exec_nginx(nginx_hosts, dest_file, bid_list, project.port, sls, roster_file, desc)
                    r['source'] = dict(r['source'], **t['source'])
                    r['result'].extend(t['result'])
                    logger.info("{}后端{}，结果：{}.".format(desc, nginx_hosts, t))
                    #break
                    del nginx_hosts[:]

        logger.info("返回结果：{}".format(r))

        Message.objects.create(type=u'Nginx负载均衡', user=username_auth(request), action='{}后端'.format(desc),
                               action_ip=user_ip(request), content='返回结果：{}'.format(r))

        return JsonResponse({'retcode':retcode, 'result': r['result']})


@login_required
@permission_required('qcloud.view_qlb')
def nginx_list(request, template_name):
    page_name = u'负载均衡'
    if request.user.is_superuser:
        projects = Project.objects.filter(lb_nginx__isnull=False).distinct()
    else:
        projects = Project.objects.filter(Q(lb_nginx__isnull=False) & Q(user_group=request.user.group)).distinct()

    return render(request, template_name, {'page_name': page_name, 'project_list': projects})


@login_required
@permission_required('qcloud.edit_qlb')
def nginx_manage(request, pid=None):
    page_name = u'后端管理'
    project = Project.objects.get(pk=pid)
    host_list = project.host_group.hosts.filter(status=True)

    return render(request, 'job_nginx_manage.html',
                  {'page_name': page_name, 'pid': pid, 'project': project, 'host_list': host_list, 'nav_tag': 'nginx_list'})

@login_required
def nginx_host(request):
    if request.is_ajax():
        id = request.POST.get('nginx_id')
        group = SaltGroup.objects.get(id=id)
        nginx_hosts = [i.ip for i in group.hosts.filter(status=True)]
        return JsonResponse(nginx_hosts, safe=False)


