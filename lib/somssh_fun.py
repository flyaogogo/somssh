#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: common.py
# @Time: 18-1-18 下午9:15

import psutil
# import socket
import commands
import platform
import json
import os
import time

from datetime import datetime, timedelta, date
from math import ceil

from somssh.settings import BASE_DIR
from userauth.views import User
from deploy.models import NetTraffic
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.utils import timezone
from deploy.models import SaltHost, Project, Job, JobLog, JobMessage
from lib.common import get_dir
from lib.mongodb_api import GetSysData


def get_token(length):
    new_token = get_user_model().objects.make_random_password(length=length,
                                                              allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
    return new_token


def get_sys_info():
    # os
    os_info = platform.platform()
    # hostname
    host_name = platform.node()
    # hostname = socket.gethostname()
    # salt version
    salt_version = commands.getoutput('salt --version')
    # cpu info
    cpu_core = psutil.cpu_count()
    # memory info
    mem = psutil.virtual_memory()
    mem_total = int(ceil(float(mem.total) / 1024 / 1024 / 1024))

    sys_info = {'os': os_info, 'hostname': host_name, 'salt_version': salt_version, 'cpu_core': cpu_core,
                'mem_total': mem_total}
    path = os.path.join(BASE_DIR, 'config/sys_info.json')
    with open(path, 'w') as f:
        json.dump(sys_info, f)

    return sys_info


def get_disk_info():
    # disk info
    disk = psutil.disk_partitions()
    disk_info = []
    for i in range(0, len(disk)):
        disk_info.append(disk[i].mountpoint)

    return {'disk_info': disk_info}


def get_sys_usage():
    # boot time
    boot_temp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_temp).strftime("%Y-%m-%d %H:%M:%S")
    online_time = time.time() - boot_temp

    # cpu usage
    cpu_percent = psutil.cpu_percent()
    # memory info
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    mem_available = mem.available
    # disk info
    disk = psutil.disk_partitions()
    disk_info = {}
    for i in range(0, len(disk)):
        info = psutil.disk_usage(disk[i].mountpoint)
        disk_info[(disk[i].mountpoint).replace('/', '')] = info

    return {'online_time': online_time, 'boot_time': boot_time, 'cpu_percent': cpu_percent, 'mem_percent': mem_percent,
            'mem_available': mem_available, 'disk_info': disk_info}


def get_net_info():
    limit = 120
    in_info = NetTraffic.objects.filter(net_type=0)[:120]
    out_info = NetTraffic.objects.filter(net_type=1)[:120]
    db = GetSysData('network', 3600, 'nettraffic', limit)
    info = db.get_data({"type": "network"}, {"_id": 0})
    info = list(info)
    x_data = []
    x_data_0 = []
    net_in = []
    net_out = []
    for i in range(1, limit):
        #x_data.append((info[i]['log_time']).strftime('%H:%M:%S'))
        x_data_0.append((info[i]['log_time']).strftime('%Y-%m-%d %H:%M:%S'))
        time_diff = (info[i]['log_time'] - info[i - 1]['log_time']).total_seconds()
        temp_in = round((info[i]['traffic_in'] - info[i - 1]['traffic_in']) / 1024.0 / time_diff, 2)
        temp_out = round((info[i]['traffic_out'] - info[i - 1]['traffic_out']) / 1024.0 / time_diff, 2)

        net_in.append(temp_in)
        net_out.append(temp_out)
    return {'x_data': sorted(x_data), 'x_data_0': sorted(x_data_0), 'net_in': net_in, 'net_out': net_out}


def net_info():
    # crontab to collect network usage
    net = psutil.net_io_counters(pernic=True)
    log_time = timezone.now()
    net_in = net[get_dir('net_interface')].bytes_recv
    net_out = net[get_dir('net_interface')].bytes_sent
    temp = [net_in, net_out]

    # r = []
    info = {"type": "network", "traffic_in": net_in, "traffic_out": net_out, "log_time": log_time}

    return info


def get_info(request):
    info = {}
    login_count = Session.objects.filter(expire_date__gte=timezone.now()).count()
    if request.user.is_superuser:
        project_count = Project.objects.count()
        project_disabled = Project.objects.filter(status=False).count()
        job_count = Job.objects.count()
        job_todo = Job.objects.filter(status=0).count()
        job_cancle = Job.objects.filter(status=2).count()
    else:
        projects = Project.objects.filter(user_group=request.user.group)
        project_count = projects.count()
        project_disabled = projects.filter(status=False).count()
        job_count = 0
        job_todo = 0
        job_cancle = 0
        for p in projects:
            jobs = Job.objects.filter(project=p)
            job_count = job_count + jobs.count()
            job_todo = job_todo + jobs.filter(status=0).count()
            job_cancle = job_cancle + jobs.filter(status=2).count()
    host_count = SaltHost.objects.count()
    host_disabled = SaltHost.objects.filter(status=False).count()
    info['project-count'] = project_count
    info['project-disabled'] = project_disabled
    info['host-count'] = host_count
    info['host-disabled'] = host_disabled
    info['job-count'] = job_count
    info['job-todo'] = job_todo
    info['job-cancle'] = job_cancle
    info['login-count'] = login_count

    return info


def get_job_info():
    x_data = []
    series = []
    y_data_succ = []
    y_data_fail = []
    for i in range(0, 14):
        n = date.today()
        d = n - timedelta(days=i)
        x_data.append(d.strftime('%Y-%m-%d'))
        jobs = JobLog.objects.filter(modify_time__contains=d)
        job_succ = jobs.filter(pub_status=True).count()
        job_fail = jobs.filter(pub_status=False).count()
        y_data_succ.append(job_succ)
        y_data_fail.append(job_fail)
    y_data_succ.reverse()
    y_data_fail.reverse()
    return {'x_data': sorted(x_data), 'y_data_succ': y_data_succ, 'y_data_fail': y_data_fail}


def get_project_info(arg):
    # 获取任务工单前10项目
    temp = {}
    projects = Project.objects.all()
    for p in projects:
        j = Job.objects.filter(project=p).count()
        temp[p] = j
    dict = sorted(temp.iteritems(), key=lambda d: d[1], reverse=True)
    return dict[:arg]


def get_user_info(arg):
    # 获取创建任务工单前10用户
    temp = {}
    users = User.objects.all()
    for u in users:
        j = Job.objects.filter(user=u).count()
        temp[u] = j
    dict = sorted(temp.iteritems(), key=lambda d: d[1], reverse=True)
    return dict[:arg]


def get_release_info(start, end):
    # 获取最近发布记录
    logs = JobMessage.objects.all()[start:end]
    logs = [
        {'id': i.pk, 'project': i.project, 'created_time': i.created_time.strftime('%Y-%m-%d %H:%M'), 'user': i.user,
         'jid': i.jid, 'msg_type': i.msg_type,
         'status': i.status, 'batch': i.batch} for i in logs]
    return logs
