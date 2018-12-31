#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: views.py.py
# @Time: 17-6-19 上午11:10

from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from salt.client.ssh.client import SSHClient

from models import SaltUser, SaltHost, SaltGroup, Pcloud, Project, ProjectBackup, Message, Job, JobLog, JobBatch, \
    JobTmpl, \
    JobRollbackLog, Region, JobMessage, JobLock  # ConfigList, ConfigBackup, ConfigLog
from forms import SaltUserForm, SaltHostForm, SaltGroupForm, PcloudForm, ProjectForm, RegionForm

from deploy.forms import JobCreateForm
from deploy.result_handle import result_handle, result_handle_2, result_handle_config

from userauth.views import username_auth, user_ip

from somssh.settings import BASE_DIR, QCLOUD_ID, QCLOUD_KEY
from svn_api import SvnSync
from lib.common import get_dir
from lib.log import log

from qcloud.qcloud_api import QcloudSDK

from datetime import datetime, timedelta, date
import time
import shutil
import threading
import os
import json
import ast
import tarfile
from ruamel import yaml

# import pysvn

# Create your views here.

import logging

logger = logging.getLogger(__name__)  # 这里用__name__通用,自动检测.

deploy_info = []


# deploy_info = {}

def svntar(fname, tmp_dir):
  t = tarfile.open(fname + ".tar.gz", "w:gz")
  for root, dir, files in os.walk(fname):
    root_ = os.path.relpath(root,start=tmp_dir)
    for file in files:
      fullpath = os.path.join(root, file)
      t.add(fullpath, arcname=os.path.join(root_,file))
  t.close()


def tag_deal(t):
    t = t.split(',')
    t = [i for i in t if i]
    return t


@login_required
def saltuser_list(request):
    saltuser = SaltUser.objects.all()

    return render(request, 'saltuser_list.html', {'saltuser': saltuser})


@login_required
@permission_required('deploy.edit_user')
def saltuser_manage(request, id=None, action=None):
    page_name = ''
    if id:
        suser = get_object_or_404(SaltUser, pk=id)
        if action == 'edit':
            page_name = u'编辑主机用户'
        if action == 'delete':
            suser.delete()
            Message.objects.create(type=u'主机用户管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, suser.username))
            return redirect('saltuser_list')
    else:
        suser = SaltUser()
        action = 'add'
        page_name = u'新增主机用户'

    if request.method == 'POST':
        form = SaltUserForm(request.POST, instance=suser)
        if form.is_valid():
            form.save()
            # suser.save()
            Message.objects.create(type=u'主机用户管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, suser.username))
            return redirect('saltuser_list')
    else:
        form = SaltUserForm(instance=suser)

    return render(request, 'saltuser_manage.html', {'form': form, 'action': action, 'page_name': page_name, 'id': id})


@login_required
def region_list(request):
    page_name = u'区域列表'
    saltuser = SaltUser.objects.all()
    regions = Region.objects.all()

    return render(request, 'region_list.html', {'regions': regions, 'page_name': page_name})


@login_required
@permission_required('deploy.edit_host')
def region_manage(request, id=None, action=None):
    page_name = u'区域管理'
    if id:
        region = get_object_or_404(Region, pk=id)
        if action == 'edit':
            page_name = u'编辑区域'
        if action == 'delete':
            region.delete()
            Message.objects.create(type=u'区域管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, region.name))
            return redirect('region_list')
    else:
        region = Region()
        action = 'add'
        page_name = u'新增区域'

    if request.method == 'POST':
        form = RegionForm(request.POST, instance=region)
        if form.is_valid():
            code = form.cleaned_data['region']
            form.save()
            content = {'region':{'grains.present':[{'value':code}]}}
            grains_dir = './media/salt/grains'
            if not os.path.exists(grains_dir):
                os.makedirs(grains_dir)
            with open('%s/%s.sls' % (grains_dir, code), 'w') as f:
                yaml.round_trip_dump(content, f, default_flow_style=False, allow_unicode=True, indent=2, block_seq_indent=2)
            Message.objects.create(type=u'主机用户管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, region.name))
            return redirect('region_list')
    else:
        form = RegionForm(instance=region)

    return render(request, 'region_manage.html',
                  {'form': form, 'action': action, 'page_name': page_name, 'id': id, 'nav_tag': 'region_list'})


@login_required
def saltgroup_list(request):
    saltgroup = SaltGroup.objects.all()

    return render(request, 'saltgroup_list.html', {'all_groups': saltgroup})


@login_required
@permission_required('deploy.edit_saltgroup')
def saltgroup_manage(request, id=None, action=None):
    page_name = u'主机组管理'

    if id:
        group = get_object_or_404(SaltGroup, pk=id)
        if action == 'edit':
            page_name = u'编辑主机组'
        if action == 'delete':
            group.delete()
            Message.objects.create(type=u'主机组管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, group.groupname))
            return redirect('saltgroup_list')
    else:
        group = SaltGroup()
        action = 'add'
        page_name = u'新增主机组'

    if request.method == 'POST':
        form = SaltGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            group.save()

            # 按主机组生成roster file，项目发布任务时选择对应组roster file
            # TODO
            # 需要更改任务执行引用的roster file
            # 将项目roster file改为主机组roster file
            roster = '# hostgroup: %s\n' % group.groupname
            roster_path = './media/salt/project_roster'
            if not os.path.exists(roster_path):
                os.makedirs(roster_path)
            for i in group.hosts.all():
                roster = roster + '''%s:
  host: %s
  port: %s
  user: %s
  passwd: %s
  #tty: True
  thin_dir: /home/%s/.salt-thin
  timeout: 60\n''' % (i.ip, i.ip, i.port, group.user, i.user.get(username=group.user).password, group.user)
            with open('%s/roster_hostgroup_%s' % (roster_path, group.id), 'w') as f:
                f.write(roster)

            Message.objects.create(type=u'主机组管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, group.groupname))
        return redirect('saltgroup_list')
    else:
        form = SaltGroupForm(instance=group)

    return render(request, 'saltgroup_manage.html',
                  {'form': form, 'action': action, 'page_name': page_name, 'id': id, 'nav_tag': 'host_group'})


@login_required
def salthost_list(request):
    salthost = SaltHost.objects.all()

    return render(request, 'salthost_list.html', {'salthost': salthost})


@login_required
@permission_required('deploy.edit_host')
def salthost_manage(request, id=None, action=None):
    # TODO: host group
    page_name = ''
    user_list = {}
    if id:
        host = get_object_or_404(SaltHost, pk=id)
        user_list = {i.id: i.username for i in host.user.all()}
        if action == 'edit':
            page_name = u'编辑主机'
        if action == 'delete':
            host.user.all().delete()
            host.delete()
            Message.objects.create(type=u'主机管理', user=username_auth(request), action=action, action_ip=user_ip(request),
                                   content=u'%s %s %s' % (action, host.hostname, host.ip))
            return redirect('salthost_list')
    else:
        host = SaltHost()
        action = 'add'
        page_name = u'新增主机'

    if request.method == 'POST':
        username = request.POST.getlist('user')
        password = request.POST.getlist('password')
        tag = time.time() * 1000
        form = SaltHostForm(request.POST, instance=host)
        while '' in username:
            username.remove('')
        try:
            username_old = [i.username for i in host.user.all()]
        except:
            username_old = []
        for i in username:
            if i in username_old:
                username.remove(i)
        if form.is_valid():
            if action == 'add':
                host = form.save(commit=False)
            elif action == 'edit':
                form.save()
            platform = form.cleaned_data['platform']
            # 腾讯云平台调用api获取主机id
            if platform == 1:
                qapi = QcloudSDK(secretid=QCLOUD_ID,
                                 secretkey=QCLOUD_KEY)
                r = qapi.cvm_list('', host.ip)
                if r['Response']['InstanceSet']:
                    host.hostid = r['Response']['InstanceSet'][0]['InstanceId']
            host.save()
            insert_list = []
            if username:
                for i in range(0, len(username)):
                    new_record = SaltUser()
                    setattr(new_record, 'username', username[i])
                    setattr(new_record, 'password', password[i])
                    setattr(new_record, 'tag', tag)
                    insert_list.append(new_record)
            if len(insert_list) > 0:
                batch = SaltUser.objects.bulk_create(insert_list)
            id_list = [i[0] for i in SaltUser.objects.filter(tag=tag).values_list('id')]
            host.user.add(*id_list)
            Message.objects.create(type=u'主机管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s %s' % (action, host.hostname, host.ip))
        return redirect('salthost_list')
    else:
        form = SaltHostForm(instance=host)

    return render(request, 'salthost_manage.html',
                  {'form': form, 'action': action, 'page_name': page_name, 'user_list': user_list, 'id': id})


@login_required
@permission_required('deploy.edit_host')
def salthost_user_update(request):
    roster_path = './media/salt/project_roster/'
    if request.is_ajax():
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        hostid = request.POST.get('hostid')
        host = SaltHost.objects.get(id=hostid)
        host_group = host.salt_host_set.all()
        saltuser = host.user.get(id=uid)
        saltuser.password = password
        saltuser.save()
        for i in host_group:
            roster_file = os.path.join(roster_path, 'roster_hostgroup_{}'.format(i.id))
            with open(roster_file, 'r') as f:
                content = yaml.load(f, Loader=yaml.RoundTripLoader)

        Message.objects.create(type=u'主机用户管理', user=username_auth(request), action='密码更新', action_ip=user_ip(request),
                               content=u'主机用户密码更新 %s' % (saltuser.username))
        return HttpResponse(json.dumps('ok'))


@login_required
@permission_required('deploy.edit_host')
def salthost_user_delete(request):
    if request.is_ajax():
        uid = request.POST.get('uid')
        hostid = request.POST.get('hostid')
        saltuser = SaltHost.objects.get(id=hostid).user.get(id=uid)
        saltuser.delete()
        Message.objects.create(type=u'主机用户管理', user=username_auth(request), action='用户删除', action_ip=user_ip(request),
                               content=u'主机用户删除 %s' % (saltuser.username))
        return HttpResponse(json.dumps('ok'))


@login_required
def ajax_hostuser(request):
    if request.is_ajax():
        arg = request.POST.get('arg')
        if arg == 'pcloud':
            tgt_select = request.POST.get('tgt_select')
        else:
            tgt_select = request.POST.get('tgt_select[]')
        saltuser = {i['username']: i['username'] for i in SaltHost.objects.get(id=tgt_select).user.values('username')}

        return HttpResponse(json.dumps(saltuser))


@login_required
def project_list(request):
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(user_group=request.user.group)

    return render(request, 'project_list.html', {'project_list': projects})


@login_required
@permission_required('deploy.edit_project')
def project_manage(request, id=None, action=None):
    page_name = ''
    radio_val = 0
    if id:
        project = get_object_or_404(Project, pk=id)
        radio_val = project.container
        if action == 'edit':
            page_name = u'编辑项目'
        if action == 'delete':
            project.delete()
            return redirect('project_list')
    else:
        project = Project()
        action = 'add'
        page_name = u'新增项目'

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            if action == 'add':
                form.save()
                config_path = './media/salt/config/%s' % (form.cleaned_data['path'])
                if not os.path.exists(config_path):
                    os.makedirs(config_path)
            elif action == 'edit':
                form.save()

            vip = form.cleaned_data['lb_vip']
            if vip:
                qapi = QcloudSDK(secretid=QCLOUD_ID,
                                 secretkey=QCLOUD_KEY)
                r = qapi.lb_query('', vip, '')
                if r['code'] == 0:
                    bid = r["loadBalancerSet"][0]['loadBalancerId']
                    project.lb_id = bid
            project.save()
            Message.objects.create(type=u'项目管理', user=username_auth(request), action=action, action_ip=user_ip(request),
                                   content=u'%s %s' % (action, project.name))

            return redirect('project_list')
        else:
            pass
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_manage.html',
                  {'form': form, 'action': action, 'page_name': page_name, 'id': id, 'radio_val': radio_val,
                   'nav_tag': 'pproject_list'})


@csrf_exempt
def ajax_host(request, pid=None):
    if request.is_ajax():
        proj = Project.objects.get(id=pid)
        host_group = proj.host_group
        hosts = {i['id']: i['hostname'] for i in host_group.hosts.values('id', 'hostname')}

        return HttpResponse(json.dumps(hosts))


def get_host(request):
    if request.is_ajax():
        user = request.POST.get('user')
        pid = request.POST.get('pid')
        hosts = {SaltHost.objects.get(user=i).id: SaltHost.objects.get(user=i).hostname for i in
                 SaltUser.objects.filter(username=user)}
        if pid != '0':
            hosts_sel = {i.pk: i.hostname for i in SaltGroup.objects.get(id=pid).hosts.all()}
            for i in hosts_sel:
                if i in hosts:
                    del hosts[i]

        return HttpResponse(json.dumps(hosts))


def log_action(request):
    pass


def log_login(request):
    pass


def salt_file_upload(request):
    host_list = SaltHost.objects.filter(host_type=False)
    if request.method == 'POST':
        host_list = request.POST.getlist('host')
        path = request.POST.get('path')
        rfile = request.FILES.getlist('file')
        dtime = datetime.now().strftime('%Y%m%d%H%M%S')
        upload = './media/salt/file.manage/upload/%s' % (dtime)
        if not os.path.exists(upload):
            os.makedirs(upload)
        for file in rfile:
            dest = open(os.path.join(upload, file.name), 'wb+')
            for chunk in file.chunks():
                dest.write(chunk)
            dest.close()
        c = SSHClient()
        data = {'spath': dtime, 'dpath': path}
        host = SaltHost.objects.get(ip=host_list[0])
        rst = c.cmd(tgt=host_list, fun='state.sls', ssh_user=host.user.all()[0].username,
                    ssh_passwd=host.user.all()[0].password,
                    roster_file='./media/salt/roster',
                    arg=['file_upload', 'pillar=%s' % json.dumps(data)], tgt_type='list')
        rst = result_handle_2(rst)

        return HttpResponse(json.dumps(rst))

    return render(request, 'salt_upload.html', {'host_list': host_list})


@login_required
@permission_required('deploy.view_job')
def job_index(request):
    form = JobCreateForm()
    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(user_group=request.user.group)

    return render(request, 'job_index.html', {'project_list': projects, 'form': form})


@login_required
@permission_required('deploy.view_job')
def job_list(request, pid=None):
    page_name = u'任务列表'

    return render(request, 'jobs_list.html',
                  {'page_name': page_name, 'pid': pid, 'nav_tag': 'job_list'})


@login_required
def job_ajax(request, pid=None):
    def _datatables(request, pid):
        datatables = request.POST
        # Ambil draw
        draw = int(datatables.get('draw'))
        # Ambil start
        start = int(datatables.get('start'))
        # Ambil length (limit)
        length = int(datatables.get('length'))
        # Ambil data search
        search = datatables.get('search[value]')
        # Set record total

        if pid:
            job_list = Job.objects.filter(project_id=pid)
        else:
            if request.user.is_superuser:
                if search in [u'已']:
                    job_list = Job.objects.filter(
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__gt=0)
                    )
                elif search in [u'已结', u'已结单']:
                    job_list = Job.objects.filter(
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=1)
                    )
                elif search in [u'已作', u'作废', u'已作废']:
                    job_list = Job.objects.filter(
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=2)
                    )
                elif search in [u'未', u'未结', u'未结单']:
                    job_list = Job.objects.filter(
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=0)
                    )
                elif search:
                    job_list = Job.objects.filter(
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search)
                    )
                else:
                    job_list = Job.objects.all()
            else:
                projects = Project.objects.filter(user_group=request.user.group)
                ## 创建空queryset
                # job_list = Job.objects.none()
                if search in [u'已']:
                    job_list = Job.objects.filter(
                        Q(project__user_group=request.user.group),
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__gt=0)
                    )
                elif search in [u'已结', u'已结单']:
                    job_list = Job.objects.filter(
                        Q(project__user_group=request.user.group),
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=1)
                    )
                elif search in [u'已作', u'作废', u'已作废']:
                    job_list = Job.objects.filter(
                        Q(project__user_group=request.user.group),
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=2)
                    )
                elif search in [u'未', u'未结', u'未结单']:
                    job_list = Job.objects.filter(
                        Q(project__user_group=request.user.group),
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search) |
                        Q(status__exact=0)
                    )
                elif search:
                    job_list = Job.objects.filter(
                        Q(project__user_group=request.user.group),
                        Q(project__name__icontains=search) |
                        Q(jid__icontains=search) |
                        Q(remark__icontains=search)
                    )
                else:
                    job_list = Job.objects.filter(project__user_group=request.user.group)


        records_total = job_list.count()
        # Set records filtered
        records_filtered = records_total

        # Atur paginator
        paginator = Paginator(job_list, length)
        cur_page = start / length + 1
        try:
            # object_list = paginator.page(draw).object_list
            object_list = paginator.page(cur_page).object_list
        except PageNotAnInteger:
            object_list = paginator.page(draw).object_list
        except EmptyPage:
            ## paginator.num_pages 总页数
            object_list = paginator.page(paginator.num_pages).object_list

        data = [
            {
                'id': j.pk,
                'url': reverse('job_exec', kwargs={'pid': j.project.pk, 'jid': j.pk}),
                'url_cancle': reverse('job_cancle', kwargs={'pid': j.project.pk, 'jid': j.pk}),
                'project': j.project.name,
                'jid': j.jid,
                'version': j.version,
                'remark': j.remark,
                'last_step': j.last_step,
                'status': j.status,
                'created_time': j.created_time,
                'user_created': j.user.first_name or j.user,
                'pub_type': j.pub_type,
            } for j in object_list
        ]

        return {
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        }

    job_list = _datatables(request, pid)

    return JsonResponse(job_list)


@login_required
@permission_required('deploy.edit_job')
def job_manage(request, pid=None, jid=None, action=None):
    page_name = u'新建任务'
    level = get_dir("log_level")
    form = JobCreateForm()
    project = get_object_or_404(Project, pk=pid)
    host_count = project.host_group.hosts.count()
    if host_count < 4 and host_count > 0:
        batch_num = host_count
    else:
        batch_num = 4
    # 过滤禁用主机
    hosts = project.host_group.hosts.filter(status=True)
    for i in JobBatch.objects.filter(jid=jid):
        hosts = hosts.exclude(pk__in=i.host.all())

    if jid:
        job = get_object_or_404(Job, pk=jid)
        if action == 'edit':
            page_name = u'编辑任务'
        if action == 'delete':
            job.delete()
            return redirect('job_list')
    else:
        job = Job()
        action = 'add'
        page_name = u'新建任务'

    # 检查是否存在未结单任务
    job_check = Job.objects.filter(Q(project_id=pid), status=0)

    version_list = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6']

    if request.method == 'GET' and request.GET.has_key('batch_num'):
        batch_num = request.GET.get('batch_num', None)
        try:
            batch_num = int(batch_num)
            if batch_num <1 or batch_num > 9:
                batch_num = 4
        except:
            batch_num = 4

    if request.method == 'POST' and request.is_ajax():
        form = JobCreateForm(request.POST)
        if form.is_valid():
            job_id = datetime.now().strftime('%j%Y%m%d%H%M%S')
            pub_type = request.POST.get('ptype', 0)
            source = request.POST.get('source', 0)
            version = request.POST.get('version', None)
            version = version.replace('\\', '')
            if int(pub_type) == 0:
                path = None
                dst = 'full'
                desc = '全量'
            else:
                path = request.POST.get('path', None)
                dst = 'increase'
                desc = '增量'
            logger.info("项目: [{0}]{1}，类型：{2}，发布版本：[{3}]".format(project.name, page_name, desc, version))
            if int(source) == 1:
                files = request.FILES.getlist('files')
                upload = './media/salt/%s/%s-%s/%s' % (dst, project.id, project.path, version)
                logger.info("开始从本地上传更新包，上传路径：[{}]".format(upload))
                if not os.path.exists(upload):
                    os.makedirs(upload)
                # file_list = []
                for file in files:
                    logger.info("开始上传[{}]...".format(file.name))
                    dest = open(os.path.join(upload, file.name), 'wb+')
                    for chunk in file.chunks():
                        dest.write(chunk)
                    dest.close()
                    logger.info("上传[{}]完成".format(file.name))

            ifreload = request.POST.get('action', 0)
            version_tips = request.POST.get('version_tips', None)

            # 批次处理
            tag_list = []
            batchs = request.POST.get('batchs', None)
            for i in range(1, int(batchs)):
                t = tag_deal(request.POST.get('to{}[]'.format(i), None))
                tag_list.append(t)

            if action == 'add':
                job.jid = job_id
                job.project = project
                job.pub_type = pub_type
                job.source = source
                job.user = request.user
                job.action_ip = user_ip(request)
            job.version = version
            job.pub_path = path
            job.ifreload = ifreload
            job.remark = version_tips
            job.save()

            for i in tag_list:
                if i:
                    tag_id = datetime.now().strftime('%j%Y%m%d%H%M%S') + str(i)
                    if action == 'add':
                        batch = JobBatch()
                        batch.jid = job
                        batch.jtag = tag_id
                        batch.tag = tag_list.index(i) + 1
                    else:
                        try:
                            batch = JobBatch.objects.get(jid=job, tag=(tag_list.index(i) + 1))
                        except:
                            batch = JobBatch()
                            batch.jid = job
                            batch.jtag = tag_id
                            batch.tag = tag_list.index(i) + 1

                    batch.save()
                    batch.host.clear()
                    batch.host.add(*i)

            logger.info("创建任务完成，写入任务列表，任务JID：[{}]".format(job.jid))
            Message.objects.create(type=u'任务管理', user=username_auth(request), action=action,
                                   action_ip=user_ip(request),
                                   content=u'%s %s' % (action, job.jid))
            return JsonResponse({'retcode': 0})
        else:
            return JsonResponse({'retcode': 1})

    return render(request, 'job_create.html',
                  {'page_name': page_name, 'project': project, 'pid': pid, 'jid': jid, 'job': job, 'batch_num':batch_num,
                   'batchs':range(1, batch_num+1), 'action': action,
                   'version_list': version_list, 'hosts': hosts, 'form': form, 'nav_tag': 'project_list', 'job_check': job_check})


def job_exec_full(host_list, project, data, sls, roster_file):
    c = SSHClient()
    # ret = {}

    result_source = c.cmd(tgt=host_list, fun='state.sls', roster_file=roster_file,
                          arg=[sls, 'pillar=%s' % json.dumps(data)], expr_form='list')

    result = result_handle(result_source)

    return {'result': result, 'source': result_source}


def job_exec_cmd(host_list, roster_file, cmd):
    c = SSHClient()
    result_source = c.cmd(tgt=host_list, fun='cmd.run', roster_file=roster_file, arg=[cmd], expr_form='list')

    return result_source


def job_rollback_full(host_list, project, dtime):
    c = SSHClient()
    data = {'puser': project.host_group.user, 'dpath': project.path, 'dtime': dtime}
    if project.container == 0:
        sls = 'job_rollback_full'
    else:
        sls = 'projectect_war_custom'
    rst = c.cmd(tgt=host_list, fun='state.sls', ssh_user=project.host_group.user,
                ssh_passwd=project.host_group.user.password,
                roster_file='./media/salt/roster',
                arg=[sls, 'pillar=%s' % json.dumps(data)], tgt_type='list')
    for _, v in rst.items():
        deploy_info.append(v)


def job_step(host_list, project, data, sls):
    c = SSHClient()
    result = c.cmd(tgt=host_list, fun='state.sls', ssh_user=project, ssh_passwd=project.host_group.user.password,
                   roster_file='./media/salt/roster',
                   arg=[sls, 'pillar=%s' % json.dumps(data)], tgt_type='list')

    result = result_handle(result)

    return result


@login_required
@permission_required('deploy.exec_job')
def job_cancle(request, pid=None, jid=None):
    if request.is_ajax():
        project = get_object_or_404(Project, pk=pid)
        job = Job.objects.get(pk=jid, project=project)
        if job.user != request.user and not request.user.is_superuser:
            return JsonResponse({'retcode': 1})
        job.status = 2
        job.save()
        Message.objects.create(type=u'任务管理', user=username_auth(request), action=u'工单作废',
                               action_ip=user_ip(request),
                               content=u'项目 %s 任务： %s <br />类型： %s<br />发布版本: %s<br />最近发布批次: %s<br />操作: 作废' % (
                                   project.name, job.jid, job.pub_type, job.version, job.last_step))
        return JsonResponse({'retcode': 0})
    return redirect('job_list')


@login_required
@permission_required('deploy.exec_job')
def job_exec(request, pid=None, jid=None):
    page_name = u'版本发布'
    level = get_dir("log_level")

    project = get_object_or_404(Project, pk=pid)
    job = Job.objects.get(pk=jid)
    batchs = JobBatch.objects.filter(jid=job)
    batch_num = len(batchs)
    last_step = int(job.last_step)
    if last_step:
        step = last_step + 1
    else:
        step = 0
    if request.is_ajax():
        if not project.status:
            logger.info("项目[{0}]已禁用，无法操作！".format(project.name))
            ret = {'code': 888}
            return JsonResponse(ret)
        logger.info("开始发布项目：[{0}]，任务JID：[{1}]".format(project.name, job.jid))
        try:
            JobLock.objects.get(job=job)
            logger.warning("该任务执行中，请勿重复操作！")
            ret = {'code': 999}
            return HttpResponse(json.dumps(ret))
        except:
            JobLock.objects.create(job=job)
            logger.info("创建任务锁！")
        batch = request.POST.get('step_number')
        batch_q = batchs.get(tag=batch)
        # 过滤禁用主机
        host_list = [i.ip for i in batch_q.host.filter(status=True)]

        dtime = datetime.now().strftime('%Y%m%d%H%M%S')

        # 如果源码包直接存放在根Url下，不带版本号，则前端填写版本号以 "----version" 为版本号
        if '----' in job.version:
            csvn = SvnSync(url='%s' % (project.code_path), username=project.code_user, password = project.code_passwd)
            version = 'svn_{}'.format(job.version.lstrip('----'))
        else:
            csvn = SvnSync(url='%s/%s' % (project.code_path, job.version), username = project.code_user, password = project.code_passwd)
            version = job.version

        roster_file = './media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id)
        if job.source == 0:
            if job.pub_type == 0:
                co_dir = os.path.join(BASE_DIR, 'media/salt/full/%s-%s/%s' % (project.id, project.path, version))
                if not os.path.exists(co_dir):
                    os.makedirs(co_dir)
                if not os.path.isfile('%s/check.out'%co_dir):
                    if project.container == 0:
                        war = '%s.war' % project.war
                        ret = csvn.getsources([war], '%s/%s' % (co_dir, war))
                    else:
                        co_dir_new = os.path.join(co_dir, project.war)
                        try:
                            os.makedirs(co_dir_new)
                        except:
                            pass
                        ret = csvn.checkall(co_dir_new)
                        try:
                            shutil.rmtree(os.path.join(co_dir_new, '.svn'))
                            svntar(co_dir_new, co_dir)
                        except:
                            pass
                else:
                    ret = {'code':0, 'exists':0}
            else:
                co_dir = os.path.join(BASE_DIR, 'media/salt/increase/%s-%s/%s' % (project.id, project.path, version))
                if not os.path.exists(co_dir):
                    os.makedirs(co_dir)
                if not os.path.isfile('%s/check.out'%co_dir):
                    ret = csvn.checkall(co_dir)
                else:
                    ret = {'code':0, 'exists':0}
            logger.info("从svn检出源码，源码存放路径：{}".format(co_dir))
            logger.info(ret)
            if ret['code'] != 0:
                logger.error("检出源码失败，删除任务锁")
                JobLock.objects.get(job=job).delete()
                return HttpResponse(json.dumps(ret))
            if ret.has_key('exists'):
                logger.info("源码已存在.")
            else:
                logger.info("检出源码完成")
                f = open(os.path.join(co_dir, 'check.out'), 'w')
                f.close()
            spath = version
        else:
            spath = job.version

        if job.pub_type == 0:
            data = {'puser': project.host_group.user, 'project': project.id, 'dpath': project.path,
                    'sname': project.war, 'dname': project.war,
                    'dtime': spath, 'ifreload': job.ifreload}
            if project.container == 0:
                sls = 'job_exec_full'
            else:
                sls = 'job_exec_full_custom'
            logger.info(
                "开始全量发布，发布批次：{0}\n发布函数：job_exec_full，参数：host_list={1}, project={2}, data={3}, sls={4}, roster_file={5}".format(
                    batch, host_list, project, data, sls, roster_file))
            rst = job_exec_full(host_list, project, data, sls, roster_file)
        else:
            data = {'puser': project.host_group.user, 'project': project.id, 'dpath': project.path, 'spath': spath,
                    'dname': job.pub_path,
                    'dtime': dtime, 'ifreload': job.ifreload}
            if project.container == 0:
                sls = 'job_exec_incr'
            else:
                sls = 'job_exec_incr_custom'
            logger.info(
                "开始增量发布，发布批次：{0}\n发布函数：job_exec_full，参数：host_list={1}, project={2}, data={3}, sls={4}, roster_file={5}".format(
                    batch, host_list, project, data, sls, roster_file))
            rst = job_exec_full(host_list, project, data, sls, roster_file)
        source = rst['source']
        rst = rst['result']

        jlog = JobLog()
        jmsg = JobMessage()
        if rst['code']:
            if int(batch) == int(batch_num):
                project.version = job.version
                project.save()
                job.status = 1
            batch_q.status = 1
            job.last_step = batch
            job.save()
            jlog.pub_status = True
            jmsg.status = True
            # add joblog id
        # 备份成功且备份路径为空时更新path字段
        if not batch_q.path and rst['cmd_backup_dir']:
            #batch_q.path = dtime
            batch_q.path = spath
        batch_q.save()
        jlog.jid = job
        jlog.batch = batch_q
        jlog.btag = '{}{}{}{}'.format(datetime.now().strftime('%Y%m%d%H%M%S'), project.id, job.id, str(batch))
        jlog.version_history = spath
        jlog.version_path = spath
        # {True:已回退, False:未回退}
        # jlog.status = 1
        jlog.content = rst['result']
        jlog.source_content = source
        jlog.user = request.user
        jlog.action_ip = user_ip(request)
        jlog.save()
        jmsg.user = username_auth(request)
        jmsg.project = project.name
        jmsg.jid = job.jid
        jmsg.action_ip = user_ip(request)
        jmsg.batch = batch_q.tag
        jmsg.content = rst['result']
        jmsg.source_content = source
        jmsg.save()
        # if rst['code']:
        rst['logid'] = jlog.id
        JobLock.objects.get(job=job).delete()
        logger.info("项目[{0}]发布完成，删除任务锁，写入发布日志，发布结果: {1}".format(project.name, source))
        return JsonResponse(rst)

    return render(request, 'job_exec.html',
                  {'page_name': page_name, 'job': job, 'pid': pid, 'jid': jid, 'batchs': batchs, 'batch_num': batch_num,
                   'project': project, 'step': step, 'nav_tag': 'job_list'})


@login_required
@permission_required('deploy.exec_job')
def job_rollback(request, pid=None, jid=None):
    page_name = u'版本回退'
    level = get_dir("log_level")
    project = get_object_or_404(Project, pk=pid)
    job = Job.objects.get(pk=jid)
    if request.is_ajax():
        if not project.status:
            logger.info("项目[{0}]已禁用，无法操作！".format(project.name))
            ret = {'code': 888}
            return JsonResponse(ret)
        batch = request.POST.get('step_number')
        logid = request.POST.get('logid')
        job_batch = JobBatch.objects.filter(jid=job)
        batch_q = job_batch.get(tag=batch)
        host_list = [i.ip for i in batch_q.host.filter(status=True)]
        jlog = JobLog.objects.get(id=logid)
        ## 原始备份
        dtime = batch_q.path
        ## 每次发布备份
        # dtime = jlog.version_history
        logger.info("开始回退项目：[{0}]，任务JID：[{1}]，回退批次：[{2}]".format(project.name, job.jid, batch))
        roster_file = './media/salt/project_roster/roster_hostgroup_%s' % (project.host_group.id)
        if job.source == 0:
            spath = dtime
        else:
            spath = job.version
        if job.pub_type == 0:
            data = {'puser': project.host_group.user, 'dpath': project.path, 'dtime': spath, 'ifreload': job.ifreload}
            if project.container == 0:
                sls = 'job_rollback_full'
            else:
                sls = 'job_rollback_full_custom'
        else:
            data = {'puser': project.host_group.user, 'dpath': project.path, 'dname': job.pub_path, 'dtime': spath,
                    'ifreload': job.ifreload}
            if project.container == 0:
                sls = 'job_rollback_incr'
            else:
                sls = 'job_rollback_incr_custom'
        logger.info(
            "回退函数：job_exec_full，参数：host_list={0}, project={1}, data={2}, sls={3}, roster_file={4}".format(host_list,
                                                                                                          project, data,
                                                                                                          sls,
                                                                                                          roster_file))
        rst = job_exec_full(host_list, project, data, sls, roster_file)
        source = rst['source']
        rst = rst['result']

        jrollback = JobRollbackLog()
        jmsg = JobMessage()
        if rst['code']:
            batch_q.status = 2
            batch_q.save()
            jlog.status = True
            jlog.save()
            job.status = 1
            job.save()
            jrollback.status = True
            jmsg.status = True
        jrollback.jid = job
        jrollback.jlog = jlog
        jrollback.content = rst['result']
        jrollback.source_content = source
        jrollback.user = request.user
        jrollback.action_ip = user_ip(request)
        jrollback.save()
        jmsg.user = username_auth(request)
        jmsg.project = project.name
        jmsg.jid = job.jid
        jmsg.action_ip = user_ip(request)
        jmsg.batch = batch_q.tag
        jmsg.content = rst['result']
        jmsg.source_content = source
        jmsg.msg_type = True
        jmsg.save()

        rst['logid'] = jlog.id
        logger.info("项目[{0}]回退完成，写入回退日志，回退结果: {1}".format(project.name, source))
        return JsonResponse(rst)


    return render(request, 'job_exec.html',
                  {'page_name': page_name, 'job': job, 'pid': pid, 'jid': jid, 'project': project})


@csrf_exempt
def job_exec_step(request, pid=None, jid=None, step=None):
    if request.is_ajax():

        return HttpResponse(json.dumps('ok'))


@csrf_exempt
def job_step_status(request, pid=None, jid=None):
    if request.is_ajax():
        step = request.POST.get('step_number', None)
        batch = JobBatch.objects.filter(jid=jid).get(tag=step)
        status = batch.status
        if not status:
            status = 1

        return HttpResponse(json.dumps(status))


@login_required
def job_history(request, jid=None):
    page_name = u'发布记录'

    return render(request, 'jobs_history_list.html', {'page_name': page_name, 'jid': jid})


@login_required
def joblog_ajax(request, jid=None):
    def _datatables(request, jid):
        datatables = request.POST
        # Ambil draw
        draw = int(datatables.get('draw'))
        # Ambil start
        start = int(datatables.get('start'))
        # Ambil length (limit)
        length = int(datatables.get('length'))
        # Ambil data search
        search = datatables.get('search[value]')
        # Set record total

        if jid:
            jlogs = JobLog.objects.filter(jid=jid)
        else:
            if request.user.is_superuser:
                if search in [u'已', u'已回', u'已回退']:
                    jlogs = JobLog.objects.filter(
                        Q(jid__project__name__icontains=search) |
                        Q(jid__jid__icontains=search) |
                        Q(status=True)
                    )
                elif search in [u'未', u'未回', u'未回退']:
                    jlogs = JobLog.objects.filter(
                        Q(jid__project__name__icontains=search) |
                        Q(jid__jid__icontains=search) |
                        Q(status=False)
                    )
                elif search in [u'失', u'失败', u'布失败', u'发布失败']:
                    jlogs = JobLog.objects.filter(
                        Q(jid__project__name__icontains=search) |
                        Q(jid__jid__icontains=search) |
                        Q(pub_status=False)
                    )
                elif search in [u'成', u'成功', u'布成功', u'发布成功']:
                    jlogs = JobLog.objects.filter(
                        Q(jid__project__name__icontains=search) |
                        Q(jid__jid__icontains=search) |
                        Q(pub_status=True)
                    )
                elif search:
                    jlogs = JobLog.objects.filter(
                        Q(jid__project__name__icontains=search) |
                        Q(jid__jid__icontains=search)
                    )
                else:
                    jlogs = JobLog.objects.all()
            else:
                projects = Project.objects.filter(user_group=request.user.group)
                # 创建空queryset
                job_list = Job.objects.none()
                for p in projects:
                    # 合并queryset
                    job_list = job_list | Job.objects.filter(project=p)
                jlogs = JobLog.objects.none()
                if search in [u'已', u'已回', u'已回退']:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(Q(jid=j),
                                                              Q(jid__project__name__icontains=search) |
                                                              Q(jid__jid__icontains=search) |
                                                              Q(status=True)
                                                              )
                elif search in [u'未', u'未回', u'未回退']:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(Q(jid=j),
                                                      Q(jid__project__name__icontains=search) |
                                                      Q(jid__jid__icontains=search) |
                                                      Q(status=False)
                                                      )
                elif search in [u'失', u'失败', u'布失败', u'发布失败']:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(Q(jid=j),
                                                      Q(jid__project__name__icontains=search) |
                                                      Q(jid__jid__icontains=search) |
                                                      Q(pub_status=False)
                                                      )
                elif search in [u'成', u'成功', u'布成功', u'发布成功']:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(Q(jid=j),
                                                      Q(jid__project__name__icontains=search) |
                                                      Q(jid__jid__icontains=search) |
                                                      Q(pub_status=True)
                                                      )
                elif search:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(Q(jid=j),
                                                      Q(jid__project__name__icontains=search) |
                                                      Q(jid__jid__icontains=search)
                                                      )
                else:
                    for j in job_list:
                        jlogs = jlogs | JobLog.objects.filter(jid=j)

        records_total = jlogs.count()
        # Set records filtered
        records_filtered = records_total

        # Atur paginator
        paginator = Paginator(jlogs, length)
        cur_page = start / length + 1
        try:
            object_list = paginator.page(cur_page).object_list
        except PageNotAnInteger:
            object_list = paginator.page(draw).object_list
        except EmptyPage:
            ## paginator.num_pages 总页数
            object_list = paginator.page(paginator.num_pages).object_list

        data = [
            {
                'id': j.pk,
                'url': reverse('job_rollback', kwargs={'pid': j.jid.project.pk, 'jid': j.jid.pk}),
                'project': j.jid.project.name,
                'jid_id': j.jid.pk,
                'jid': j.jid.jid,
                'version': j.jid.version,
                'tag': j.batch.tag,
                'status_pub': j.pub_status,
                'status_roll': j.status,
                'modify_time': j.modify_time,
                'user_created': j.jid.user.first_name or j.jid.user,
                'user_exec': j.user.first_name or j.user,
                'batch_status': j.batch.status,
            } for j in object_list
        ]

        return {
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data,
        }

    jlogs = _datatables(request, jid)

    return JsonResponse(jlogs)


@login_required
def job_history_detail(request):
    if request.is_ajax():
        jid = request.GET.get('jid')
        jlog = JobLog.objects.get(pk=jid)
        rst = jlog.content.replace('\r\n', '')
        rst = ast.literal_eval(rst)
        return JsonResponse(rst)


@login_required
def job_rollback_detail(request):
    if request.is_ajax():
        jid = request.GET.get('jid')
        jlog = JobLog.objects.get(pk=jid)
        jrollback = JobRollbackLog.objects.filter(jlog=jlog)[0]
        rst = jrollback.content.replace('\r\n', '')
        rst = ast.literal_eval(rst)
        return JsonResponse(rst)


@login_required
@permission_required('deploy.edit_job')
def job_tmpl(request, pid=None, action=None):
    page_name = u'任务模板'
    project = get_object_or_404(Project, pk=pid)
    hosts = project.host_group.hosts.all()
    host_count = project.host_group.hosts.count()
    if host_count < 4 and host_count > 0:
        batch_num = host_count
    else:
        batch_num = 4
    if request.method == 'GET' and request.GET.has_key('batch_num'):
        batch_num = request.GET.get('batch_num', None)
        try:
            batch_num = int(batch_num)
            if batch_num <1 or batch_num > 9:
                batch_num = 4
        except:
            batch_num = 4

    if request.method == 'POST' and request.is_ajax():
        if action == 'delete':
            job_tmpl = JobTmpl.objects.filter(project=project)
            if len(job_tmpl) == 0:
                return JsonResponse({'retcode': 1})
            job_tmpl.delete()
            Message.objects.create(type=u'任务管理', user=username_auth(request), action=action, action_ip=user_ip(request),
                                   content=u'删除任务模板 %s' % (project.name))
            return JsonResponse({'retcode': 0})
        tag_list = []
        batchs = request.POST.get('batchs', None)
        for i in range(0, int(batchs)):
            t = tag_deal(request.POST.get('to%s[]'%(i+1), None))
            tag_list.append(t)

        for i in tag_list:
            if i:
                job_tmpl = JobTmpl()
                job_tmpl.project = project
                job_tmpl.jtag = '%s-%s' % (project.id, tag_list.index(i) + 1)
                job_tmpl.tag = tag_list.index(i) + 1
                try:
                    job_tmpl.save()
                except:
                    return JsonResponse({'retcode': 1})
                job_tmpl.host.add(*i)
        Message.objects.create(type=u'任务管理', user=username_auth(request), action=action, action_ip=user_ip(request),
                               content=u'创建任务模板 %s' % (project.name))
        return JsonResponse({'retcode': 0})

    return render(request, 'job_create_tmpl.html',
                  {'page_name': page_name, 'project': project, 'pid': pid, 'batch_num':batch_num, 'batchs':range(1, batch_num+1), 'action': action,
                   'hosts': hosts, 'nav_tag': 'project_list'})


@login_required
@permission_required('deploy.edit_job')
# @permission_required('deploy.edit_job'，login_url='/deploy/job/index/')
# @permission_required('deploy.edit_job', raise_exception=True)
def job_manage_quick(request):
    # page_name = u'快速创建任务'
    level = get_dir("log_level")
    if request.method == 'POST' and request.is_ajax():
        form = JobCreateForm(request.POST)
        if form.is_valid():
            pid = request.POST.get('project_id')
            project = get_object_or_404(Project, pk=pid)
            job = Job()
            job_id = datetime.now().strftime('%j%Y%m%d%H%M%S')
            pub_type = request.POST.get('ptype', 0)
            source = request.POST.get('source', 0)
            version = request.POST.get('version', None)

            # 检查是否存在未结单任务
            job_check = Job.objects.filter(Q(project_id=pid), status=0)
            if job_check:
                return JsonResponse({'retcode': 3})

            job_tmpl = JobTmpl.objects.filter(project=project)
            if len(job_tmpl) <= 0:
                return JsonResponse({'retcode': 2})
            if int(pub_type) == 0:
                path = None
                dst = 'full'
                desc = '全量'
            else:
                path = request.POST.get('path', None)
                dst = 'increase'
                desc = '增量'
            logger.info("项目[{0}]快速新建{1}任务，发布版本：[{2}]".format(project.name, desc, version))
            if int(source) == 1:
                files = request.FILES.getlist('files')
                path = request.POST.get('path', None)
                upload = './media/salt/%s/%s-%s/%s' % (dst, project.id, project.path, version)
                logger.info("开始从本地上传更新包，上传路径：{}".format(upload))
                if not os.path.exists(upload):
                    os.makedirs(upload)
                # file_list = []
                for file in files:
                    dest = open(os.path.join(upload, file.name), 'wb+')
                    logger.info("开始上传{}...".format(file.name))
                    for chunk in file.chunks():
                        dest.write(chunk)
                    dest.close()
                    logger.info("上传{}完成".format(file.name))
            ifreload = request.POST.get('action', 0)
            version_tips = request.POST.get('version_tips', None)

            job.jid = job_id
            job.project = project
            job.version = version
            job.pub_type = pub_type
            job.source = source
            job.pub_path = path
            job.ifreload = ifreload
            # job.status = False
            job.remark = version_tips
            job.user = request.user
            job.action_ip = user_ip(request)
            job.save()

            for i in JobTmpl.objects.filter(project=project):
                tag_id = datetime.now().strftime('%j%Y%m%d%H%M%S') + str(i.tag)
                batch = JobBatch()
                batch.jid = job
                batch.jtag = tag_id
                batch.tag = i.tag
                batch.save()
                batch.host.add(*i.host.all())

            logger.info("快速创建任务完成，写入任务列表")
            Message.objects.create(type=u'任务管理', user=username_auth(request), action='add', action_ip=user_ip(request),
                                   content=u'快速创建 %s' % (job.jid))
            return JsonResponse({'retcode': 0})
        else:
            return JsonResponse({'retcode': 1})


@login_required
def job_host(request):
    if request.is_ajax():
        jid = request.POST.get('jid')
        batch = request.POST.get('batch')
        obj = Job.objects.get(pk=jid)
        try:
            host_list = [{'hostname': i.hostname, 'ip': i.ip, 'user': obj.project.host_group.user} for i in
                         JobBatch.objects.filter(jid=obj).get(tag=batch).host.all()]
            return JsonResponse(host_list, safe=False)
        except:
            host_list = None
        return JsonResponse(host_list, safe=False)


@login_required
def job_help(request):
    return render(request, 'job_help.html', {})

@login_required
def about(request):
    return render(request, 'about.html', {})

@login_required
def release_log(request):
    if request.user.is_superuser:
        logs = JobMessage.objects.all()[:300]

        if request.method == 'GET':
            if request.GET.has_key('aid'):
                aid = request.get_full_path().split('=')[1]
                log_detail = JobMessage.objects.get(id=aid)

                return render(request, 'log_job_release_detail.html', {'log_detail': log_detail})

        return render(request, 'log_job_release.html', {'all_logs': logs})
    else:
        # raise Http404
        rst = '<script type = "text/javascript">alert("无权限查看！");' + \
              'self.location.href="/";</script>'
        return HttpResponse(rst)


@login_required
def host_flush(request):
    pass


config_info = {}


def host_config_push(host, project, data, sls):
    global config_info
    c = SSHClient()
    r = {}
    for i in host.user.all():
        ret = c.cmd(tgt=host.ip, fun='state.sls', ssh_user=i.username, ssh_passwd=i.password,
                    roster_file='./media/salt/roster', arg=[sls], expr_form='list')
        for _, v in ret.items():
            r[i.username] = v
    config_info[host.ip] = r


def host_config_refresh(host, project, data, sls):
    global config_info
    c = SSHClient()
    r = {}
    for i in host.user.all():
        ret = c.cmd(tgt=host.ip, fun='saltutil.sync_grains', ssh_user=i.username, ssh_passwd=i.password,
                    roster_file='/opt/somssh/media/salt/roster')
        for _, v in ret.items():
            r[i.username] = v
    config_info[host.ip] = r


def multiple_job(host_list, project, data, sls, myfun):
    global config_info
    threads = []
    loop = 0
    count = len(host_list)
    for i in range(0, count, 2):
        keys = range(loop * 2, (loop + 1) * 2, 1)

        # 实例化线程
        for i in keys:
            if i >= count:
                break
            else:
                t = threading.Thread(target=myfun,
                                     args=(host_list[i], project, data, sls))
                threads.append(t)
        # 启动线程
        for i in keys:
            if i >= count:
                break
            else:
                threads[i].start()
        # 等待并发线程结束
        for i in keys:
            if i >= count:
                break
            else:
                threads[i].join()
        loop = loop + 1

    return config_info
