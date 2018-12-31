#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: views.py
# @Time: 17-12-25 下午5:37

from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from salt.client.ssh.client import SSHClient

from models import ConfigList, ConfigBackup, ConfigLog

from deploy.models import SaltHost, Region, Project
from userauth.views import user_ip
from deploy.result_handle import result_handle_config

from userauth.views import username_auth
from somssh.settings import BASE_DIR

from lib.common import SomsParse

import ConfigParser
import time
import datetime
import shutil
import threading
import os
import json


# Create your views here.

def get_config(request):
    content = ''
    if request.is_ajax():
        fname = request.POST.get('fname')
        pid = request.POST.get('project')
        p = Project.objects.get(id=pid)
        # try:
        with open('./media/salt/config/%s-%s/%s' % (pid, p.path, fname), 'r') as f:
            content = f.read()
        return HttpResponse(content)


@login_required
@permission_required('sconf.edit_config')
def push_config(request):
    c = SSHClient()
    if request.is_ajax():
        rst = {}
        regions = Region.objects.all()
        action = request.GET.get('action')

        rst = {}
        for i in regions:
            region = i.region
            roster = ''
            roster_path = './media/salt/region_sls'
            if not os.path.exists(roster_path):
                os.makedirs(roster_path)
            host_list = SaltHost.objects.filter(region=i)
            for h in host_list:
                for u in h.user.all():
                    roster = roster + '''%s-%s:
  host: %s
  port: %s
  user: %s
  passwd: %s
  thin_dir: /home/%s/.salt-thin
  timeout: 30\n''' % (h.ip, u.username, h.ip, h.port, u.username, u.password, u.username)
            with open('%s/roster_%s' % (roster_path, region), 'w') as f:
                f.write(roster)

            if action == 'push':
                r = {}
                ret = c.cmd(tgt='*', fun='state.sls', roster_file='%s/roster_%s' % (roster_path, region),
                            arg=['grains.%s' % region])
                rst = dict(rst, **ret)
            elif action == 'refresh':
                ## refresh grains
                ret = c.cmd(tgt='*', fun='saltutil.sync_grains', roster_file='%s/roster_%s' % (roster_path, region))
                rst = dict(rst, **ret)
            else:
                raise Http404
        return HttpResponse(json.dumps(rst))


def get_config_version(request):
    if request.is_ajax():
        fname = request.GET.get('filename')
        pid = request.GET.get('project')
        p = Project.objects.get(id=pid)
        clist = ConfigList.objects.filter(project=p).get(name=fname)
        cbaks = [{'version': i.path, 'tips': i.remark} for i in ConfigBackup.objects.filter(name=clist)]
        return HttpResponse(json.dumps(cbaks))


@login_required
@permission_required('sconf.edit_config')
def project_config(request, template_name, pid=None):
    page_name = u'配置文件'
    content_sls = ''
    content_config = ''

    project = Project.objects.get(pk=pid)
    config_path = './media/salt/config/%s-%s' % (project.id, project.path)
    config_list = [i['name'] for i in ConfigList.objects.filter(project=project).values('name')]
    project_id = (project.path).replace('.', '-')
    roster_file = './media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id)
    # 过滤禁用主机
    host_list = project.host_group.hosts.filter(status=True)
    regions = Region.objects.all()
    rst = {'retcode': 0}
    if request.is_ajax():
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'update':
                filename = request.POST.get('config')
                content_config = request.POST.get('content_config')
                content_sls = request.POST.get('content_sls')
                config_path = './media/salt/config/%s-%s' % (project.id, project.path)
                file = filename.split('.')[0]
                ## 备份原文件
                shutil.copy('%s/%s.jinja' % (config_path, filename), '%s/%s.jinja.bakup' % (config_path, filename))
                shutil.copy('%s/%s.ini' % (config_path, filename), '%s/%s.ini.bakup' % (config_path, filename))

                try:
                    with open('%s/%s.ini' % (config_path, filename), 'w') as f:
                        f.write(content_sls)
                except:
                    content_config = 'File %s/%s not exists.' % (config_path, filename)

                try:
                    with open('%s/%s.jinja' % (config_path, filename), 'w') as f:
                        f.write(content_config)
                except:
                    content_config = 'File %s/%s not exists.' % (config_path, filename)

                return HttpResponse(json.dumps('ok'))

            if action == 'release':
                hosts = request.POST.get('hosts')
                filename = request.POST.get('config')
                #### test ####
                path = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                # 重命名备份文件
                shutil.copy('%s/%s.jinja.bakup' % (config_path, filename),
                            '%s/%s.jinja.%s' % (config_path, filename, path))
                shutil.copy('%s/%s.ini.bakup' % (config_path, filename),
                            '%s/%s.ini.%s' % (config_path, filename, path))
                c = SSHClient()

                cfg = SomsParse()
                cfg.read(os.path.join(config_path, '{}.ini'.format(filename)))
                data = cfg.as_dict()
                data['puser'] = project.host_group.user
                data['dpath'] = project.path
                data['dtime'] = path
                data['pub_path'] = project.path
                data['filename'] = filename
                data['ctype'] = project.container
                data['project'] = project.id

                rst_source = c.cmd(tgt=hosts, fun='state.sls', roster_file=roster_file,
                                   arg=['job_config', 'pillar=%s' % json.dumps(data)], expr_form='list')
                #### end #####
                rst = result_handle_config(rst_source)

                # 创建更新列表
                cbak = ConfigBackup()
                cbak.name = ConfigList.objects.filter(project=project).get(name=filename)
                cbak.path = path
                cbak.content = rst
                cbak.save()

                # 记录操作日志
                ConfigLog.objects.create(user=username_auth(request), project=project.name, config=filename,
                                         action_ip=user_ip(request), content=rst, source_content=rst_source,
                                         msg_type=False)
                return HttpResponse(json.dumps(rst))

            if action == 'rollback':
                hosts = request.POST.get('hosts')
                filename = request.POST.get('config')
                version = request.POST.get('config_ver')
                # 还原对应版本文件
                shutil.copy('%s/%s.jinja.%s' % (config_path, filename, version),
                            '%s/%s.jinja' % (config_path, filename))
                c = SSHClient()
                data = {'puser': project.host_group.user, 'project': project.id, 'dpath': project.path,
                        'dtime': version,
                        'pub_path': project.path,
                        'filename': filename, 'ctype': project.container}
                rst_source = c.cmd(tgt=hosts, fun='state.sls', roster_file=roster_file,
                                   arg=['job_config_rollback', 'pillar=%s' % json.dumps(data)], expr_form='list')
                #### end #####
                rst = result_handle_config(rst_source)
                ConfigLog.objects.create(user=username_auth(request), project=project.name, config=filename,
                                         action_ip=user_ip(request), content=rst, source_content=rst_source,
                                         msg_type=True)
                return HttpResponse(json.dumps(rst))

        filename = request.GET.get('config')

        config_path = os.path.join(BASE_DIR, './media/salt/config/%s-%s' % (project.id, project.path))
        if not os.path.exists(config_path):
            os.makedirs(config_path)

        file = filename.split('.')[0]
        action = request.GET.get('action')
        if action == 'get':
            try:
                with open('%s/%s.ini' % (config_path, filename), 'r') as f:
                    content_sls = f.read()
            except:
                content_sls = 'File %s/%s not exists, created?' % (config_path, filename)
                rst['retcode'] = 1
            try:
                with open('%s/%s.jinja' % (config_path, filename), 'r') as f:
                    content_config = f.read()
            except:
                content_config = 'File %s/%s not exists, created?' % (config_path, filename)
                rst['retcode'] = 1
        else:
            config = ConfigParser.RawConfigParser()
            region_query = Region.objects.all()
            if len(region_query) == 0:
                rst['retcode'] = 3
                return JsonResponse(rst)
            for i in region_query:
                config.add_section(i.region)
                config.set(i.region, 'name', i.name)
                config.set(i.region, 'region', i.region)
            with open(os.path.join(config_path, '%s.ini' % filename), 'w') as f:
                config.write(f)

            try:
                with open('%s/%s.jinja' % (config_path, filename), 'r') as f:
                    content_config = f.read()
            except:
                with open('%s/%s.jinja' % (config_path, filename), 'w') as f:
                    f.write(
                        "{% set region = grains['region'] %}\n#key不存在时报错：pillar[region]['key']\n" +
                        "#key不存在时使用默认值：salt['pillar.get'](region + ':key', 'default')")
            # 记录文件
            clist = ConfigList()
            clist.name = filename
            clist.project = project
            clist.tag = '%s-%s' % (filename, project.id)
            clist.save()

            rst['retcode'] = 2

        rst['sls'] = content_sls
        rst['config'] = content_config

        return HttpResponse(json.dumps(rst))

    return render(request, template_name,
                  {'page_name': page_name, 'pid': pid, 'all_hosts': host_list, 'all_regions': regions,
                   'project': project,
                   'project_id': project_id, 'config_list': config_list, 'nav_tag': 'project_list'})


@login_required
def project_config_check(request, pid=None):
    project = Project.objects.get(pk=pid)
    config_list = [i['name'] for i in ConfigList.objects.filter(project=project).values('name')]
    host_list = project.host_group.hosts.all()

    if request.is_ajax():
        filename = request.POST.get('filename')
        host = request.POST.get('host')

    return render(request, 'job_project_config_check.html',
                  {'pid': pid, 'all_hosts': host_list, 'project': project, 'config_list': config_list})
