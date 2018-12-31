#!/usr/bin/env python
# coding: utf8
'''
@author: qitan
@contact: qqing_lai@hotmail.com
@file: myfilter.py
@time: 2017/3/30 15:32
@desc:
'''

from django import template
from django.contrib.auth.models import Group
from userauth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

# from deploy.models import SaltGroup

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg, 'required': 'required'})


@register.filter(name='group_minions')
def minions(value):
    '''
    分组列表中显示所有主机
    '''

    try:
        group_minions = value.hosts.all()
        return group_minions
    except:
        return ''


@register.filter(name='group_users')
def all_users(group):
    '''
    分组列表中显示所有主机
    '''

    try:
        # all_users = group.user_set.all()
        all_users = User.objects.filter(group=group)
        return all_users
    except:
        return ''


@register.filter(name='department_users')
def all_department_users(pk):
    '''
    部门所有用户
    '''

    try:
        all_department_users = Department.objects.get(pk=pk).user_set.all()
        return all_department_users
    except:
        return ''


@register.filter(name='user_departments')
def user_departments(user, level):
    '''
    用户所属部门（组）
    '''

    try:
        # user = User.objects.get(pk=pk)
        if level == "1":
            department = {i.id: i.deptname for i in user.department.filter(level=1)}
        else:
            department = {i.id: i.deptname for i in user.department.filter(~Q(level=1))}
        return sorted(department.items())
    except:
        return ''


@register.filter(name='user_groups')
def all_user_groups(pk):
    '''
    用户所属组
    '''

    try:
        user_group = [i.name for i in Group.objects.filter(user=pk)]
        return user_group
    except:
        return ''


@register.filter(name='department_subs')
def all_dept_subs(pk):
    '''
    子部门
    '''
    try:
        all_depts = ["<li>%s</li>" % i.deptname for i in Department.objects.filter(parent_id=pk)]
        return all_depts
    except:
        return ''


@register.filter(name='is_super')
def user_is_super(pk):
    '''
    是否为超级用户
    '''
    if pk:
        return User.objects.get(pk=pk).is_superuser
    else:
        return None


@register.filter(name='str_split')
def show_str(value, arg):
    '''
    分割权限控制中远程命令、远程目录列表
    '''
    if value:
        str_list = value.split(arg)
        return str_list
    else:
        return ''


@register.filter(name='list_item')
def show_item(value, arg):
    '''
    获取列表中指定项
    '''
    if value:
        return value[arg]
    else:
        return ''


@register.filter(name='project_host')
def show_host(project):
    return project.host_group.hosts.all()


@register.filter(name='divide_1024')
def divide_1024(value):
    if value:
        if value > 1024 * 1024:
            value = '%s GB' % round(float(value) / 1024 / 1024, 2)
        elif value > 1024:
            value = '%s MB' % round(float(value) / 1024, 2)
        else:
            value = '%s KB' % int(value)
    return value


@register.filter(name='truncatehanzi')
def truncatehanzi(value, arg):
    """    
    Truncates a string after a certain number of words including    
    alphanumeric and CJK characters.     
    Argument: Number of words to truncate after.    
    """
    try:
        bits = []
        for x in arg.split(u':'):
            if len(x) == 0:
                bits.append(None)
            else:
                bits.append(int(x))
        if int(x) < len(value):
            return value[slice(*bits)] + '...'
        return value[slice(*bits)]

    except (ValueError, TypeError):
        return value  # Fail silently.


@register.filter(name='nginx_host')
def nginx_host(value):
    nginx_hosts = value.hosts.filter(status=True)
    return nginx_hosts


