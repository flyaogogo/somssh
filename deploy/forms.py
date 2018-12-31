#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: forms.py
# @Time: 17-6-20 上午10:51

from django import forms
from models import SaltHost, SaltGroup, SaltUser, Pcloud, Project, Region
from userauth.models import UserGroup


class SaltUserForm(forms.ModelForm):
    class Meta:
        model = SaltUser
        fields = '__all__'
        widgets = {
            'user': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
        }


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
        }


class SaltHostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SaltHostForm, self).__init__(*args, **kwargs)
        #self.fields['region'].widget.choices = Region.objects.values_list('pk', 'name')
        r = [(i['pk'], i['name']) for i in Region.objects.values('pk', 'name')]
        self.fields['region'].widget.choices = [('', '------')]  + r

    class Meta:
        PF_CHOICES = ((0, u'IDC机房'), (1, u'腾讯云'), (2, u'阿里云'))
        model = SaltHost
        # fields = ('hostname', 'ip', 'port', 'user', 'password', 'remark')
        fields = ('hostname', 'ip', 'port', 'host_type', 'status', 'platform', 'region', 'remark')
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'ip': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'required': 'requierd'}),
            'platform': forms.RadioSelect(choices=PF_CHOICES),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control'})
        }


class SaltGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SaltGroupForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.choices = list(set([(i['username'], i['username']) for i in SaltUser.objects.values('username')]))

    class Meta:
        model = SaltGroup
        fields = ('groupname', 'user', 'is_nginx', 'hosts')
        widgets = {
            'groupname': forms.TextInput(attrs={'class':'form-control', 'required':'required'}),
            'user': forms.Select(attrs={'class': 'form-control', 'required': 'required', 'onchange': 'ajax_host("0");'}),
            'hosts':forms.SelectMultiple(attrs={'class': 'form-control', 'required': 'required', 'disabled': 'true', 'style': 'display:none;'}),
        }


class PcloudForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PcloudForm, self).__init__(*args, **kwargs)
        self.fields['ip'].widget.choices = SaltHost.objects.filter(host_type=False).values_list('pk', 'hostname')
        self.fields['db_host'].widget.choices = SaltHost.objects.filter(host_type=True).values_list('pk', 'hostname')

    class Meta:
        model = Pcloud
        # fields = '__all__'
        exclude = ('publish_status',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'ip': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'user': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'type': 'hidden'}),
            # 'status': forms.ChoiceField(),
            'root_path': forms.TextInput(
                attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'project-root-tomcat'}),
            'service_path': forms.TextInput(
                attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'project-service-tomcat'}),
            'db_host': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'db_user': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'type': 'hidden'}),
            'sid': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'memcached': forms.TextInput(
                attrs={'class': 'form-control', 'required': 'required', 'placeholder': '127.0.0.1:11211'}),
            'remark': forms.Textarea(attrs={'class': 'form-control'})
        }


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['user_group'].widget.choices = UserGroup.objects.values_list('pk', 'group_name')
        self.fields['lb_nginx'].widget.choices = SaltGroup.objects.filter(is_nginx=True).values_list('pk', 'groupname')

    def clean_code_passwd(self):
        instance = getattr(self, 'instance', None)
        if not self.cleaned_data['code_passwd']:
            return instance.code_passwd
        else:
            return self.cleaned_data['code_passwd']

    class Meta:
        TYPE_CHOICES = ((0, 'Tomcat'), (1, 'Play'))
        model = Project
        #fields = '__all__'
        exclude = ('created_time', 'modify_time', 'lb_id')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'host_group': forms.Select(attrs={'class': 'form-control'}),
            'path': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'mycode-tomcat'}),
            'code_path': forms.TextInput(attrs={'class': 'form-control', 'required': 'required',
                                                'placeholder': 'https://svn.imaojia.com/mycode/'}),
            'code_user': forms.TextInput(attrs={'class': 'form-control'}),
            'code_passwd': forms.PasswordInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'}),
            'user_group': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'required': 'requierd'}),
            'war': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            #'lb_nginx': forms.Select(attrs={'class': 'form-control'}),
            'lb_nginx': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'lb_vip': forms.TextInput(attrs={'class': 'form-control'}),
            'container': forms.RadioSelect(choices=TYPE_CHOICES),
            'remark': forms.Textarea(attrs={'class': 'form-control'})
        }


class JobCreateForm(forms.Form):
    CHOICES = ((0, u'重启',), (1, u'不重启',))
    version = forms.CharField(label=u'发布版本号', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg: ver1.1',}))# 'required': 'required', 'pattern': '[A-z0-9._-]{2,}'}))
    version_tips = forms.CharField(label=u'发布版本说明', required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    action = forms.ChoiceField(label=u'进程管理', widget=forms.RadioSelect, choices=CHOICES,  initial=0)





