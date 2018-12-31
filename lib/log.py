#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: log.py
# @Time: 18-1-24 下午12:45

import logging
import os
from somssh.settings import BASE_DIR

dic = {"debug": logging.DEBUG,
       "warning": logging.WARNING,
       "info": logging.INFO,
       "critical": logging.CRITICAL,
       "error": logging.ERROR,
       }


def log(log_name, level="info", path=None):

    if path:
        log_path = path+'/'
    else:
        log_path = '{}/logs/'.format(BASE_DIR)

    logging.basicConfig(level=dic[level],
                # format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                format='%(asctime)s|%(levelname)s|%(message)s',
                datefmt='%Y%m%d %H:%M:%S',
                filename=log_path+log_name,
                filemode='ab+')
    return logging.basicConfig
