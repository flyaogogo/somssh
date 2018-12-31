#!/usr/bin/env python
# coding: utf8
'''
@author: qitan
@contact: qqing_lai@hotmail.com
@file: myuserauth.py
@time: 2017/3/30 15:31
@desc:
'''

from django import template
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from userauth.models import User, UserGroup
from deploy.models import SaltHost, Project

register = template.Library()

def show_permissions(aid, perm_type):
    '''
    获取所有权限
    '''
    select_permissions_dict = {}
    permissions = Permission.objects.filter(
        Q(content_type__app_label__exact='asset') |
        Q(content_type__app_label__exact='deploy') |
        Q(content_type__app_label__exact='sconf') |
        Q(content_type__app_label__exact='sprocess') |
        Q(content_type__app_label__exact='qcloud') |
        Q(content_type__app_label__exact='userauth')).values('pk', 'name')
    permissions_dict = {i['pk']:i['name'] for i in permissions}

    if aid and perm_type == 'user':
        user = User.objects.get(pk=aid)
        select_permissions_dict = {i['pk']: i['name'] for i in user.user_permissions.values('pk', 'name')}
        try:
            select_permissions_group_dict = {i['pk']: '%s（继承组）'%i['name'] for i in user.group.permissions.values('pk', 'name')}
            select_permissions_dict = dict(select_permissions_dict, **select_permissions_group_dict)
        except:
            pass
    elif aid and perm_type == 'user_group':
        group = Group.objects.get(pk=aid)
        select_permissions_dict = {i['pk']:i['name'] for i in group.permissions.values('pk','name')}
    # elif aid and perm_type == 'department':
    #     select_permissions_dict = {i['pk']:i['name'] for i in Department.objects.get(pk=aid).permissions.values('pk', 'name')}

    for i in select_permissions_dict:
        if i in permissions_dict:
            del permissions_dict[i]

    return {'permissions_dict':permissions_dict, 'select_permissions_dict':select_permissions_dict}

register.inclusion_tag('tag_permissions.html')(show_permissions)


def show_users(aid, value):
    '''
    获取用户
    '''

    select_users_dict = {}
    users_dict = {i['pk']: i['first_name'] for i in User.objects.values('pk', 'first_name')}

    if aid and value=='user_group':
        select_users_dict = {i['pk']:i['first_name'] for i in UserGroup.objects.get(pk=aid).user_group_set.values('pk', 'first_name')}
    elif aid and value=='department':
        # aid here is department name
        select_users_dict = {i['pk']:i['first_name'] for i in Department.objects.get(pk=aid).user_set.values('pk', 'first_name')}
    for i in select_users_dict:
        if i in users_dict:
            del users_dict[i]

    return {'users_dict':users_dict, 'select_users_dict':select_users_dict}

register.inclusion_tag('tag_users.html')(show_users)


def show_user_groups(aid):
    '''
    获取用户组
    '''
    select_user_groups_dict = {}
    user_groups_dict = {i['pk']: i['group_name'] for i in UserGroup.objects.values('pk', 'group_name')}

    if aid:
        select_user_groups_dict = {i['pk']:i['group_name'] for i in User.objects.get(pk=aid).group.values('pk', 'group_name')}

    for i in select_user_groups_dict:
        if i in user_groups_dict:
            del user_groups_dict[i]

    return {'user_groups_dict':user_groups_dict, 'select_user_groups_dict':select_user_groups_dict}

register.inclusion_tag('tag_user_groups.html')(show_user_groups)


def show_minions(aid, arg):
    '''
    获取用户组或Salt分组主机
    :param aid:
    :return:
    '''
    select_minions_dict = {}
    minions = {i['pk']: i['hostname'] for i in SaltHost.objects.values('pk', 'hostname')}

    if aid and arg == 'user_group':
        select_minions_dict = {i['pk']:i['hostname'] for i in SaltHost.objects.filter(user_group=aid).values('pk', 'hostname')}

    for i in select_minions_dict:
        if i in minions:
            del minions[i]

    return {'minions':sorted(minions.items()), 'select_minions_dict':sorted(select_minions_dict.items())}
register.inclusion_tag('tag_minions.html')(show_minions)

