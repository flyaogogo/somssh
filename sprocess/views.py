# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from models import ProcessList, ProcessMessage

from deploy.models import Project, SaltHost
from deploy.views import job_exec_full
from userauth.views import user_ip

from userauth.views import username_auth

from somssh.settings import BASE_DIR

from salt.client.ssh.client import SSHClient

import os
import json

import logging
logger = logging.getLogger('django')

# Create your views here.

@login_required
def project_process(request):
    page_name = u'项目进程'
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(user_group=request.user.group)

    return render(request, 'job_process_list.html', {'page_name': page_name, 'project_list': projects})


@login_required
@permission_required('sprocess.edit_process')
def project_process_manage(request, template_name, pid=None):
    page_name = '进程管理'

    if pid:
        project = Project.objects.get(pk=pid)
        plist = ProcessList.objects.filter(project=project)
        roster_file = os.path.join(BASE_DIR, 'media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id))

        if request.is_ajax():
            host = request.POST.get('hid')
            action = request.POST.get('action')
            if action == 'flush':
                ## 手动刷新单台机器进程信息
                if not project.status:
                    return HttpResponse(json.dumps({'retcode': 255}))
                r = process_info(project, host)
                return JsonResponse(r)
            if action == 'flush_all':
                ## 手动刷新所有机器进程信息，过滤禁用主机
                host_list = [i.ip for i in project.host_group.hosts.filter(status=True)]
                if not project.status:
                    return HttpResponse(json.dumps({'retcode': 255}))
                r = process_info(project, host_list)
                return JsonResponse(r)
            if action == 'flush_auto':
                ## 页面ajax定时刷新
                r = {
                    i.pk: '%s %s %s %s %s %s %s %s' % (i.process_user, i.process_pid, i.process_ppid, i.process_cpu_per,
                                                       i.process_mem_per, i.process_rmem, i.process_start,
                                                       i.process_etime)
                    for i in ProcessList.objects.filter(project=project)}
                return JsonResponse(r)
            ## 进程启动、重启、停止
            data = {'puser': project.host_group.user, 'dpath': project.path, 'ctype': project.container}
            sls = 'tomcat_%s' % action
            rst = job_exec_full(host, project, data, sls, roster_file)

            for _, v in rst['source'][host]['return'].items():
                rst['result'] = 'Retcode: %s<br />%s' % (
                    rst['source'][host]['retcode'], v['name'].replace('\n', '<br />'))
            ProcessMessage.objects.create(user=username_auth(request), project=project.name, action=action,
                                          action_ip=user_ip(request), content=rst['result'],
                                          source_content=rst['source'])
            return JsonResponse(rst['source'])

        return render(request, template_name,
                      {'page_name': page_name, 'process_list': plist, 'project': project, 'nav_tag': 'project_process'})


def process_info(project, hosts):
    roster_file = os.path.join(BASE_DIR, 'media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id))
    c = SSHClient()
    if project.container == 0:
        ## 显示长用户名
        rst = c.cmd(hosts, 'cmd.run',
                    [
                        'ps -o ruser=LONGUSERNAME12 -eo pid,ppid,pcpu,pmem,rss,lstart,etime,cmd|grep config.file=/home/%s/%s/conf|grep -v grep|awk \'{print $1,$2,$3,$4,$5,$6,$8,$9,$10,$12}\'' % (
                            project.host_group.user, project.path)],
                    roster_file=roster_file, expr_form='list')

    else:
        logger.info('Process Collect')
        rst = c.cmd(hosts, 'cmd.run', [
            'if [ -f /home/%s/%s/RUNNING_PID ];then ps -o ruser=LONGUSERNAME12 -eo pid,ppid,pcpu,pmem,rss,lstart,etime,cmd|grep `cat /home/%s/%s/RUNNING_PID`|grep -v grep|awk \'{print $1,$2,$3,$4,$5,$6,$8,$9,$10,$12}\';else exit 1;fi' % (
                project.host_group.user, project.path, project.host_group.user, project.path)], roster_file=roster_file,
                    expr_form='list')
    logger.info('Result: %s'%rst)
    result = {}
    for k, v in rst.items():
        try:
            plist = ProcessList.objects.get(tag='%s-%s' % (project.id, k))
        except:
            plist = ProcessList()
            plist.tag = '%s-%s' % (project.id, k)
        plist.project = project
        plist.host = SaltHost.objects.get(ip=k)
        if v['retcode'] == 0 and v['return']:
            rlist = v['return'].split(' ')
            t = 0
            if "-" in rlist[9]:
                t = t + int(rlist[9].split("-")[0]) * 24 * 3600
                d = rlist[9].split("-")[1]
            else:
                d = rlist[9].split("-")[0]
            d = d.split(":")
            if len(d) == 3:
                t = t + int(d[0]) * 3600 + int(d[1]) * 60 + int(d[2])
            else:
                t = t + int(d[0]) * 60 + int(d[1])
            plist.process_user = rlist[0]
            plist.process_pid = rlist[1]
            plist.process_ppid = rlist[2]
            plist.process_cpu_per = rlist[3]
            plist.process_mem_per = rlist[4]
            plist.process_rmem = rlist[5]
            plist.process_start = '%s%s-%s' % (rlist[6], rlist[7], rlist[8])
            plist.process_etime = t
            r = "%s %s %s %s %s %s %s%s-%s %s" % (
                rlist[0], rlist[1], rlist[2], rlist[3], rlist[4], rlist[5], rlist[6], rlist[7], rlist[8], t)
        else:
            r = "None None None None None None None None"
            plist.process_user = None
            plist.process_pid = None
            plist.process_ppid = None
            plist.process_cpu_per = None
            plist.process_mem_per = None
            plist.process_rmem = None
            plist.process_start = None
            plist.process_etime = None
        plist.save()
        plist = ProcessList.objects.get(tag='%s-%s' % (project.id, k))
        result[plist.pk] = r

    return result


def log_tail(request):
    if request.is_ajax():
        pid = request.POST.get('pid')
        host = request.POST.get('host')
        project = Project.objects.get(pk=pid)
        roster_file = os.path.join(BASE_DIR, 'media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id))
        data = {'puser': project.host_group.user, 'dpath': project.path}
        sls = 'log_tail'
        c = SSHClient()
        r = c.cmd(tgt=host, fun='state.sls', roster_file=roster_file, arg=[sls, 'pillar=%s' % json.dumps(data)],
                  expr_form='list')
        ret = ''
        for _, v in r.items():
            for _, v1 in v['return'].items():
                ret = v1['changes']['stdout']
        return JsonResponse({'retcode': 0, 'result': ret})


@login_required
def process_log(request):
    '''
    审计日志
    '''
    if request.user.is_superuser:
        page_name = u'进程日志'
        logs = ProcessMessage.objects.all()[:300]

        if request.method == 'GET':
            if request.GET.has_key('aid'):
                aid = request.get_full_path().split('=')[1]
                log_detail = ProcessMessage.objects.filter(id=aid)
                return render(request, 'log_job_process_detail.html',
                              {'log_detail': log_detail})

        return render(request, 'log_job_process.html',
                      {'page_name': page_name, 'all_logs': logs})
    else:
        # raise Http404
        rst = '<script type = "text/javascript">alert("无权限查看！");' + \
              'self.location.href="/";</script>'
        return HttpResponse(rst)


