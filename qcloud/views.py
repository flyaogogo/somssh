# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from qcloud.models import QcloudCVM, QcloudLB
from qcloud_api import QcloudSDK
from deploy.models import Project
from somssh.settings import QCLOUD_ID, QCLOUD_KEY

import logging
logger = logging.getLogger('django')


# Create your views here.

@login_required
def qcvm_list(request):
    qcvm = QcloudCVM.objects.all()
    return render(request, 'qcvm_list.html', {'qcvm': qcvm})


@login_required
def qcvm_import(request):
    if request.is_ajax():
        qapi = QcloudSDK(secretid=QCLOUD_ID, secretkey=QCLOUD_KEY)
        ret = qapi.cvm_list('', 0)

        return JsonResponse({'retcode': 0})


@login_required
@permission_required('deploy.exec_job')
def qlb_modify(request):
    if request.is_ajax():
        lbid = request.POST.get('lbid')
        bid_list = request.POST.getlist('bid_list[]')
        weight = request.POST.get('weight')
        logger.info("开始设置负载均衡云主机权重为{}".format(weight))
        if 'None' in bid_list:
            logging.info("存在无id的云主机，停止操作！")
            return JsonResponse({'retcode': 2})
        qapi = QcloudSDK(secretid=QCLOUD_ID, secretkey=QCLOUD_KEY)
        ret = qapi.lb_backend_modify('', lbid, bid_list, weight)
        logger.info("返回结果：{}".format(ret))
        try:
            if ret['code'] == 0:
                return JsonResponse({'retcode': 0})
            else:
                return JsonResponse({'retcode': 1})
        except:
            logger.info("设置云主机权重出错！")



@login_required
def qlb_list(request, template_name):
    page_name = u'负载均衡'
    if request.user.is_superuser:
        projects = Project.objects.filter(lb_vip__isnull=False)
        return render(request, template_name, {'page_name': page_name, 'project_list': projects})


@login_required
def qlb_manage(request, pid=None):
    page_name = u'后端管理'
    if request.user.is_superuser:
        project = Project.objects.get(pk=pid)
        host_list = project.host_group.hosts.filter(status=True)
        return render(request, 'job_qlb_manage.html',
                      {'page_name': page_name, 'pid': pid, 'project': project, 'host_list': host_list,
                       'nav_tag': 'qlb_list'})

