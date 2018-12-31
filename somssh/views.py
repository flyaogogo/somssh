# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from somssh.settings import BASE_DIR

from salt.client.ssh.client import SSHClient

from lib.somssh_fun import get_sys_info, get_disk_info, get_sys_usage, get_net_info, get_release_info, get_user_info, \
    get_job_info, get_info, get_project_info, get_token

import psutil
import os
import json
import ConfigParser


# Create your views here.

@login_required
def index(request):
    # 获取cpu、内存及操作系统等信息
    try:
        with open(os.path.join(BASE_DIR, 'config/sys_info.json'), 'r') as f:
            index_info = json.load(f)
    except:
        index_info = get_sys_info()
    # 获取磁盘分区信息
    disk_info = get_disk_info()
    index_info['disk_info'] = disk_info['disk_info']
    # 获取记录数量
    num = 10
    index_info['num'] = num
    # 获取项目任务前10
    project_info = get_project_info(10)
    index_info['project_info'] = project_info
    # 获取创建任务前10的用户
    user_info = get_user_info(10)
    index_info['user_info'] = user_info
    # 获取最近发布记录
    log_info = get_release_info(0, num)
    index_info['log_info'] = log_info

    if request.is_ajax():
        req_type = request.POST.get('req_type')
        if req_type == 'sys':
            sys_usage = get_sys_usage()
            return JsonResponse(sys_usage)
        elif req_type == 'appchart':
            job_info = get_job_info()
            return JsonResponse(job_info)
        elif req_type == 'netinfo':
            net_info = get_net_info()
            return JsonResponse(net_info)
        elif req_type == 'log_info':
            last_id = request.POST.get('last_id')
            start_id = int(last_id) * num
            end_id = start_id + num
            log_info = get_release_info(start_id, end_id)
            return JsonResponse(log_info, safe=False)
        else:
            info = get_info(request)
            return JsonResponse(info)
    return render(request, 'index.html', index_info)


@login_required
@csrf_exempt
def sys_config(request):
    page_name = u'配置管理'
    if request.user.is_superuser:
        net_info_path = os.path.join(BASE_DIR, 'config/net_interface.json')
        try:
            with open(net_info_path, 'r') as f:
                net_info = json.load(f)
        except:
            net = psutil.net_io_counters(pernic=True)
            net_info = [k for k,_ in net.items()]
            with open(net_info_path, 'w') as f:
                json.dump(net_info, f)
        cfg_path = os.path.join(BASE_DIR, 'config/system_global.conf')
        config = ConfigParser.ConfigParser()
        try:
            with open(cfg_path, 'r') as cfg:
                config.readfp(cfg)
                # api token
                token = config.get('token', 'token')
                # log level
                log_level = config.get('log', 'log_level')
                # network interface
                net_interface = config.get('network', 'net_interface')
                # mongodb info
                mongodb_ip = config.get('mongodb', 'mongodb_ip')
                mongodb_port = config.get('mongodb', 'mongodb_port')
                mongodb_user = config.get('mongodb', 'mongodb_user')
                mongodb_pwd = config.get('mongodb', 'mongodb_pwd')
                mongodb_collection = config.get('mongodb', 'collection')
        except:
            pass
        if request.method == 'POST':
            if request.is_ajax():
                token = get_token(16)
                return JsonResponse({'retcode': 0, 'token': token})
            else:
                # api token
                token = request.POST.get('token')
                # log level
                log_level = request.POST.get('log_level')
                # network interface
                net_interface = request.POST.get('net_interface')
                # mongodb info
                mongodb_ip = request.POST.get('mongodb_ip')
                mongodb_port = request.POST.get('mongodb_port')
                mongodb_user = request.POST.get('mongodb_user')
                mongodb_pwd = request.POST.get('mongodb_pwd')
                mongodb_collection = request.POST.get('mongodb_collection')
                config = ConfigParser.RawConfigParser()
                config.add_section('token')
                config.set('token', 'token', token)
                config.add_section('log')
                config.set('log', 'log_level', log_level)
                config.add_section('network')
                config.set('network', 'net_interface', net_interface)
                config.add_section('mongodb')
                config.set('mongodb', 'mongodb_ip', mongodb_ip)
                config.set('mongodb', 'mongodb_port', mongodb_port)
                config.set('mongodb', 'mongodb_user', mongodb_user)
                config.set('mongodb', 'mongodb_pwd', mongodb_pwd)
                config.set('mongodb', 'collection', mongodb_collection)
                try:
                    with open(cfg_path, 'wb') as cfg:
                        config.write(cfg)
                except:
                    pass
        return render(request, 'system_config.html', locals())


def test_mongo():
    from somssh.model import TestModel
    tt = TestModel(test_key='d1', test_value='v1')
    tt.save()


