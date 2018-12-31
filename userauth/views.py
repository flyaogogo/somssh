#!/usr/bin/env python
# coding: utf8
'''
@author: qitan
@contact: qqing_lai@hotmail.com
@file: views.py.py
@time: 2017/3/30 16:07
@desc:
'''

import functools
import warnings

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
)
from django.utils.deprecation import (
    RemovedInDjango20Warning,  # RemovedInDjango110Warning,
)
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.conf import settings as djsettings

from deploy.models import Message

import os
import json
import pyotp
import time
from qrcode import QRCode, constants
from somssh.settings import BASE_DIR
from .forms import *

from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)  # 这里用__name__通用,自动检测.


def time_forbidden_simple(period_list):
    now = int(time.strftime('%H%M%S'))
    for range in period_list:
        r = range.replace(':','').split('-')
        if int(r[0]) <= now <= int(r[1]):
            return True
    return False


def time_forbidden(period_list):
    now = time.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S")
    for range in period_list:
        r = range.split("-")
        if time.strptime(r[0], "%H:%M:%S") <= now <= time.strptime(r[1], "%H:%M:%S") or time.strptime(r[0],
                                                                                                  "%H:%M:%S") >= now >= time.strptime(
                r[1], "%H:%M:%S"):
            return True
    return False


def get_qrcode(skey, username):
    filepath = os.path.join(BASE_DIR, '/media/qrcode/')
    data = pyotp.totp.TOTP(skey).provisioning_uri(username, issuer_name=u'SOMS')
    qr = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=6,
        border=4
    )
    try:
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        img.save(filepath + username + '.png')
        return True
    except Exception, e:
        print e
        return False


def googleMfa(skey, verify_code):
    t = pyotp.TOTP(skey)
    result = t.verify(verify_code)

    return result


def deprecate_current_app(func):
    """
    Handle deprecation of the current_app parameter of the views.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            warnings.warn(
                "Passing `current_app` as a keyword argument is deprecated. "
                "Instead the caller of `{0}` should set "
                "`request.current_app`.".format(func.__name__),
                RemovedInDjango20Warning
            )
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)

    return inner


def username_auth(request):
    try:
        if request.user.first_name:
            return request.user.first_name
        else:
            return request.user
    except:
        return request.POST.get('username')


def username_obj(obj):
    if obj.first_name:
        return obj.first_name
    else:
        return obj


def user_ip(request):
    '''
    获取用户IP
    '''

    ip = ''
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


@login_required
def index(request):
    return render(request, 'soms_help.html', {})


@deprecate_current_app
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=AuthenticationForm):
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))
    verify_err = ''
    login_err = ''
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if request.POST.has_key('login'):
            if form.is_valid():
                verify_code = request.POST.get('verify_code')
                if form.get_user() and form.get_user().is_active:
                    ## disable mfa
                    # if form.get_user().is_superuser and not form.get_user().mfa:
                    #     result = True
                    # else:
                    #     result = googleMfa(form.get_user().mfa, verify_code)
                    result = True
                    if not result:
                        verify_err = u'验证码错误'
                        try:
                            cache.incr('uid:verify:{}'.format(form.get_user().id), 1)
                        except:
                            cache.set('uid:verify:{}'.format(form.get_user().id), 1, timeout=300)
                        count = cache.get('uid:verify:{}'.format(form.get_user().id))
                        if count >= 3:
                            login_err = u'用户已被禁用，请联系管理员！'
                            form.get_user().is_active = False
                            form.get_user().save()
                            Message.objects.create(type='UserAuth', user=username_auth(request), action=u'用户登录',
                                                   action_ip=user_ip(request),
                                                   content=u'用户{}[{}]登录失败，验证码错误累计3次，用户已锁定.'.format(
                                                       username_auth(request), request.user))
                    else:
                        time_check = time_forbidden_simple(['11:30:00-13:30:00', '17:30:00-19:00:00'])
                        time_check = False
                        if not time_check:
                            # Ensure the user-originating redirection url is safe.
                            if not is_safe_url(url=redirect_to, host=request.get_host()):
                                redirect_to = resolve_url(djsettings.LOGIN_REDIRECT_URL)
                            auth_login(request, form.get_user())
                            Message.objects.create(type='UserAuth', user=username_auth(request), action=u'用户登录',
                                                   action_ip=user_ip(request),
                                                   content='用户登录 %s[%s]' % (username_auth(request), request.user))
                            return HttpResponseRedirect(redirect_to)
                        else:
                            login_err = u'高峰时间段禁止登录发布平台！'
            else:
                Message.objects.create(type='UserAuth', user=username_auth(request), action=u'用户登录',
                                       action_ip=user_ip(request), content=u'用户登录失败 %s' % username_auth(request))
    else:
        form = authentication_form(request)
    return render(request, 'registration/login.html',
                  {'form': form, 'title': '用户登录', 'verify_err': verify_err, 'login_err': login_err})


@deprecate_current_app
def logout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    Message.objects.create(type='UserAuth', user=username_auth(request), action=u'用户退出', action_ip=user_ip(request),
                           content='用户退出 %s[%s]' % (username_auth(request), request.user))
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if (redirect_field_name in request.POST or
                redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        return HttpResponseRedirect(next_page)

    return HttpResponseRedirect('/')


@login_required
def user_list(request):
    all_users = User.objects.all()
    return render(request, 'userauth_user_list.html', {'all_users': all_users})


@login_required
def group_list(request):
    all_groups = UserGroup.objects.all()
    return render(request, 'userauth_group_list.html', {'all_groups': all_groups})


@login_required
def user_manage(request, aid=None, action=None):
    if request.user.has_perms(['userauth.view_user', 'userauth.edit_user']):
        page_name = ''
        if aid:
            user = get_object_or_404(User, pk=aid)
            group_old = user.group
            if action == 'edit':
                page_name = '编辑用户'
            if action == 'delete':
                user.delete()
                Message.objects.create(type=u'用户管理', user=username_auth(request), action=u'删除用户',
                                       action_ip=user_ip(request),
                                       content=u'删除用户 %s，用户名 %s' % (username_obj(user), user.username))
                return redirect('user_list')
        else:
            user = User()
            group_old = user.group
            action = 'add'
            page_name = '新增用户'

        if request.method == 'POST':
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                perm_select = request.POST.getlist('perm_sel')
                perm_select = [int(i) for i in perm_select]
                user_group = request.POST.getlist('group')
                user_group = [i for i in user_group if i]
                if action == 'add' or action == 'edit':
                    # 获取原属组权限并清空授给用户的权限
                    if not user_group and group_old:
                        try:
                            g = [i.id for i in group_old.permissions.all()]
                            perm_select = list(set(perm_select).difference(set(g)))
                        except:
                            pass
                    form.save
                    if password1 and password1 == password2:
                        user.set_password(password1)
                    skey = pyotp.random_base32()
                    if not user.mfa:
                        user.mfa = skey
                        get_qrcode(skey, user.username)
                    user.save()
                    if action == 'edit':
                        user.user_permissions.clear()
                    # 授予用户权限
                    user.user_permissions.add(*perm_select)
                    # 添加用户至Group组，授权用户该组权限
                    try:
                        user.groups.add(*user_group)
                    except:
                        pass
                    Message.objects.create(type=u'用户管理', user=username_auth(request), action=page_name,
                                           action_ip=user_ip(request),
                                           content=u'%s %s，用户名 %s' % (
                                               page_name, username_obj(user), user.username))
                    return redirect('user_list')
        else:
            form = UserForm(instance=user)

        return render(request, 'userauth_user_manage.html',
                      {'form': form, 'page_name': page_name, 'action': action, 'aid': aid, 'nav_tag': 'user_list'})
    else:
        raise Http404


@login_required
def group_manage(request, aid=None, action=None):
    if request.user.has_perms(['userauth.view_user', 'userauth.edit_user']):
        page_name = ''
        if aid and action:
            group = get_object_or_404(UserGroup, pk=aid)
            if action == 'edit':
                page_name = '编辑用户组'
            if action == 'delete':
                group.delete()
                Message.objects.create(type=u'用户分组管理', user=username_auth(request), action=u'删除分组',
                                       action_ip=user_ip(request),
                                       content=u'删除分组 %s' % group.name)
                return redirect('user_group_list')
        else:
            group = UserGroup()
            action = 'add'
            page_name = '新增用户组'

        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                host_select = request.POST.getlist('host_sel')
                perm_select = request.POST.getlist('perm_sel')
                if action == 'add' or action == 'edit':
                    form.save
                    group.save()
                    if action == 'edit':
                        group.host_usergroup_set.clear()
                        group.permissions.clear()
                    group.host_usergroup_set.add(*host_select)
                    group.permissions.add(*perm_select)

                    Message.objects.create(type=u'用户分组管理', user=username_auth(request), action=page_name,
                                           action_ip=user_ip(request),
                                           content=u'%s %s' % (page_name, group.name))
                    return redirect('user_group_list')
        else:
            form = GroupForm(instance=group)

        return render(request, 'userauth_group_manage.html',
                      {'form': form, 'page_name': page_name, 'action': action, 'aid': aid, 'nav_tag': 'ugroup_list'})
    else:
        raise Http404


@login_required
def ajax_user_groups(request):
    user_groups = {i['pk']: i['group_name'] for i in
                   User.objects.get(pk=request.user.pk).group.values('pk', 'group_name')}

    return HttpResponse(json.dumps(user_groups))


@login_required
def audit_log(request, log_type):
    '''
    审计日志
    '''
    if request.user.is_superuser:
        if log_type == 'userauth':
            page_name = u'登录日志'
            logs = Message.objects.filter(type='UserAuth')[:300]
        else:
            page_name = u'操作日志'
            logs = Message.objects.exclude(type='UserAuth')[:300]

        if request.method == 'GET':
            if request.GET.has_key('aid'):
                aid = request.get_full_path().split('=')[1]
                log_detail = Message.objects.filter(id=aid)
                return render(request, 'log_userauth_audit_detail.html',
                              {'log_detail': log_detail, 'log_type': log_type})

        return render(request, 'log_userauth_audit.html',
                      {'page_name': page_name, 'all_logs': logs, 'log_type': log_type})
    else:
        # raise Http404
        rst = '<script type = "text/javascript">alert("无权限查看！");' + \
              'self.location.href="/";</script>'
        return HttpResponse(rst)
