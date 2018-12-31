#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: result_handle.py
# @Time: 17-9-26 下午7:30

# import logging
#
# logger = logging.getLogger('django')

def dict_del(d, k_list):
    for k in k_list:
        try:
            d.pop(k)
        except:
            pass

def result_handle(c):
    result = {}
    return_code = 1
    jid = None
    update_war = False
    file_backup_dir = False
    cmd_backup_dir = False
    rst = {}
    for k, v in c.items():
        d = ['', '', '', '', '']
        index = None
        try:
            if int(v['retcode']) != 0:
                return_code = 0
        except:
            return_code = 0
        # if v['retcode'] != 14:
        if 'fun_args' in v:
            for k1, v1 in v['return'].items():
                kt = k1.split('_|-')
                kp = kt[0] + '-' + kt[1]
                if 'State was not run because none of the onchanges' in v1['comment'] or 'is in the correct state' in \
                        v1['comment'] or 'One or more requisite failed' in v1['comment'] or 'not present' in v1[
                    'comment']:
                    if kp != 'file-backup_dir':
                        v['retcode'] = 2
                        v1['result'] = False
                        return_code = 0
                # 字典转为数组，按操作步骤排序
                if kp == 'cmd-tomcat_startup':
                    index = 4
                elif kp == 'file-update_war' or kp == 'cmd-update_war' or kp == 'archive-update_war':
                    index = 3
                elif kp == 'cmd-backup_dir' and v1['result']:
                    # 判断备份是否成功
                    cmd_backup_dir = True
                    index = 2
                elif kp == 'file-backup_dir':
                    index = 1
                elif kp == 'cmd-tomcat_shutdown':
                    index = 0
                # # 替换key
                # v['return']['[[{}]]'.format(kp)] = v['return'].pop(k1)
                d[index] = {'[[{}]]'.format(kp):v1}
                # 删除多余key
                dict_del(v1, ['name', '__sls__', '__run_num__', '__id__'])
            # 替换return值为数组
            v['return'] = d
        # 删除多余key
        dict_del(v, ['fun_args','fun','id','out'])

    result['code'] = return_code
    result['cmd_backup_dir'] = cmd_backup_dir
    result['result'] = c
    return result


def result_handle_2(c):
    rst = {}
    for k, v in c.items():
        b = {}
        # if v['retcode'] != 14:
        if 'fun_args' in v:
            # if 'return' in v:
            aa = ''
            p1 = ''
            p2 = ''
            p3 = ''
            p0 = ''
            q1 = ''
            q2 = ''
            q3 = ''
            q0 = ''
            rdict = {}
            for k1, v1 in v['return'].items():
                try:
                    kid = v1['__id__']
                except:
                    kid = ''
                try:
                    kname = v1['name']
                except:
                    kname = ''
                try:
                    ktime = v1['start_time']
                except:
                    ktime = ''
                try:
                    kdura = v1['duration']
                except:
                    kdura = ''
                if v1['result']:
                    ret = 'true'
                else:
                    ret = 'false'
                aa = 'Comment: %s\nResult: %s\n__id__: %s\nName: %s\nStart_time: %s\nDuration: %s' % (
                    v1['comment'], ret, kid, kname, ktime, kdura)
                kt = k1.split('_|-')
                kp = kt[0] + '-' + kt[1]
                rdict[kt[0] + '-' + kt[1]] = aa
                if kp == 'file-update_war':
                    if v1['result']:
                        p0 = '[%s]: %s' % (kp, aa)
                    else:
                        q0 = '[%s]: %s' % (kp, aa)
                elif kp == 'file-backup_dir':
                    if v1['result']:
                        p1 = '[%s]: %s' % (kp, aa)
                    else:
                        q1 = '[%s]: %s' % (kp, aa)
                elif kp == 'cmd-backup_dir':
                    if v1['result']:
                        p2 = '[%s]: %s' % (kp, aa)
                    else:
                        q2 = '[%s]: %s' % (kp, aa)
                elif kp == 'file-file_delete':
                    if v1['result']:
                        p3 = '[%s]: %s' % (kp, aa)
                    else:
                        q3 = '[%s]: %s' % (kp, aa)


            b['stdout'] = '%s%s%s%s' % (p0, p1, p2, p3)
            b['stderr'] = '%s%s%s%s' % (q0, q1, q2, q3)
            b['retcode'] = v['retcode']
            rst[k] = b


        else:
            rst[k] = v

    return rst


def result_handle_config(c):
    rst = {}
    for k, v in c.items():
        result = {}
        result['retcode'] = v['retcode']
        try:
            comment = ''
            stderr = ''
            stdout = ''
            diff = ''
            for k1, v1 in v['return'].items():
                comment = comment + '<br />' + v1['comment'] + '<br />'
                try:
                    result['result'] = v1['result']
                except:
                    result['result'] = ''
                try:
                    stderr = stderr + '<br />' + v1['changes']['stderr'] + '<br />'
                except:
                    result['stderr'] = ''
                try:
                    stdout = stdout + '<br />' + v1['changes']['stdout'].replace('\n', '<br />') + '<br />'
                except:
                    result['stdout'] = ''
                try:
                    diff = diff + '<br />' + v1['changes']['diff'].replace('\n', '<br />') + '<br />'
                except:
                    result['diff'] = ''
            result['comment'] = comment
            result['stderr'] = stderr
            result['stdout'] = stdout
            result['diff'] = diff
        except:
            result['stderr'] = v['stderr']
            result['diff'] = ''

        rst[k] = result
        
    return rst
