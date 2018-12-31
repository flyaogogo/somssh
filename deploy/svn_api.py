#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: svn_api.py
# @Time: 17-10-20 下午3:26

import pysvn
# import os
import sys
import time

import logging
logger = logging.getLogger('deploy.views')

class SvnSync(object):
    def __init__(self, url, username, password):
        self.__svn_user = username
        self.__svn_password = password
        self.__svn_url = url

        # 日志条数
        self.__log_num = 10

    # 获取日志
    def getLog(self):

        try:
            client = pysvn.Client()
            # 参考 http://pysvn.tigris.org/docs/pysvn_prog_ref.html#pysvn_client_callback_get_login
            client.callback_get_login = self.svn_login

            # 参考 http://pysvn.tigris.org/docs/pysvn_prog_ref.html#pysvn_client_log
            log = client.log(self.__svn_url, revision_start=pysvn.Revision(pysvn.opt_revision_kind.head),
                             limit=self.__log_num)

            for info in log:
                logAuthor = info.author
                logTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.date))

        except Exception, e:
            logger.error('svn error: %s' % e)

    def getsources(self, filelist, destpath):
        '''Get the files listed in filelist from svnsrv and put it at dest.'''
        try:
            client = pysvn.Client()
            client.callback_get_login = self.svn_login
            logger.info("Checking out sources, please wait.")

            for elem in filelist:
                try:
                    client.export('%s/%s' % (self.__svn_url, elem), destpath)
                except:
                    r = "SVN client error: %s\nURL: %s, destination: %s" % (
                    sys.exc_value, '%s/%s' % (self.__svn_url, elem), destpath)
                    logger.error(r)
                    return {'code': -1, 'result': {'Checkout sources': {'retcode': 254, 'stderr': r}}}
            r = "Checkout finished."
            logger.info(r)
            return {'code': 0, 'result': {'Checkout sources': {'retcode': 0, 'stdout': r}}}
        except Exception, e:
            logger.error('svn error: %s' % e)
            return {'code': -1, 'result': {'Checkout sources': {'retcode': 254, 'stderr': e}}}

    def checkall(self, destpath):
        '''Get the files listed in filelist from svnsrv and put it at dest.'''
        try:
            client = pysvn.Client()
            client.callback_get_login = self.svn_login
            logger.info("Checking out sources, please wait.")

            try:
                client.checkout(self.__svn_url, destpath)
            except:
                r = "SVN client error: %s\nURL: %s, destination: %s" % (
                    sys.exc_value, '%s' % (self.__svn_url), destpath)
                logger.error(r)
                return {'code': -1, 'result': {'Checkout sources': {'retcode': 254, 'stderr': r}}}
            r = "Checkout finished."
            logger.info(r)
            return {'code': 0, 'result': {'Checkout sources': {'retcode': 0, 'stdout': r}}}
        except Exception, e:
            logger.error('svn error: %s' % e)
        return {'code': -1, 'result': {'Checkout sources': {'retcode': 254, 'stderr': e}}}

    # svn 登录验证函数
    def svn_login(self, realm, username, may_save):
        return True, self.__svn_user, self.__svn_password, False
