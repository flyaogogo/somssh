#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: common.py
# @Time: 18-1-23 下午5:50

from django.http import HttpResponse

from somssh.settings import BASE_DIR

import ConfigParser
import json


class SomsParse(ConfigParser.ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d


def get_dir(args):
    config = ConfigParser.RawConfigParser()
    cfg_path = '%s/config/system_global.conf'%BASE_DIR
    with open(cfg_path, 'r') as cfg:
        config.readfp(cfg)
        token = config.get('token', 'token')
        log_level = config.get('log', 'log_level')
        net_interface = config.get('network', 'net_interface')
        mongodb_ip = config.get('mongodb', 'mongodb_ip')
        mongodb_port = config.get('mongodb', 'mongodb_port')
        mongodb_user = config.get('mongodb', 'mongodb_user')
        mongodb_pwd = config.get('mongodb', 'mongodb_pwd')
        mongodb_collection = config.get('mongodb', 'collection')
    if args:
        return vars()[args]
    else:
        return HttpResponse(status=403)


def token_verify():

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            set_token = get_dir('token')
            error_info = "Post forbidden, your token error!!"
            if request.method == 'POST':
                post_token = json.loads(request.body)
                if set_token == post_token["token"]:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse(error_info, status=403)
            if request.GET:
                post_token = request.GET['token']
                if set_token == post_token:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse(error_info, status=403)
            return HttpResponse(error_info, status=403)

        return _wrapped_view

    return decorator
