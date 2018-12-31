#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: qcloud_api.py
# @Time: 18-1-4 下午1:55


from QcloudApi.qcloudapi import QcloudApi

import json


class QcloudSDK(object):
    '''
    module: 设置需要加载的模块
    已有的模块列表：
    cvm      对应   cvm.api.qcloud.com
    cdb      对应   cdb.api.qcloud.com
    lb       对应   lb.api.qcloud.com
    trade    对应   trade.api.qcloud.com
    sec      对应   csec.api.qcloud.com
    image    对应   image.api.qcloud.com
    monitor  对应   monitor.api.qcloud.com
    cdn      对应   cdn.api.qcloud.com
    '''

    def __init__(self, secretid, secretkey):
        self.__sid = secretid
        self.__skey = secretkey
        # config: 云API的公共参数
        self.__config = {
            'Region': 'ap-guangzhou',
            'secretId': str(self.__sid),
            'secretKey': str(self.__skey),
            'method': 'POST',
            'SignatureMethod': 'HmacSHA256'
        }

    def postRequest(self, module, region, action, action_params):
        try:
            service = QcloudApi(module, self.__config)
            # 重新设置请求的region
            # bj，广州:gz，上海:sh，香港:hk，北美:ca
            region_list = ['bj', 'gz', 'sh', 'hk', 'ca']
            if region in region_list:
                service.setRegion(region)

            # 重新设置请求的method
            # method = 'GET'
            # service.setRequestMethod(method)
            # 生成请求的URL，不发起请求
            # print(service.generateUrl(action, action_params))

            # 调用接口，发起请求
            ret = service.call(action, action_params)
            null = None
            false = False
            print(ret)
            return json.loads(ret)

        except Exception as e:
            import traceback
            print('traceback.format_exc():\n%s' % traceback.format_exc())

    def cvm_list(self, region, lip):
        '''
        获取云主机列表
        :return: 
        '''
        module = 'cvm'
        action = 'DescribeInstances'

        action_params = {
            'Version': '2017-03-12',
            'Limit': 1,
            'Filters.1.Name': 'private-ip-address',
            'Filters.1.Values.1': lip
        }

        ret = self.postRequest(module, region, action, action_params)
        return ret

    def lb_list(self, region):
        '''
        获取lb列表
        :param region: 
        :return: 
        '''
        module = 'lb'
        action = 'DescribeLoadBalancers'

        # 接口参数
        action_params = {
            'limit': 10
        }

        ret = self.postRequest(module, region, action, action_params)
        return ret

    def lb_list_backend(self, region, lbid):
        '''
        获取lb后端机器
        :param region: 
        :param vip: 
        :return: 
        '''
        module = 'lb'
        action = 'DescribeLoadBalancerBackends'

        # 接口参数
        action_params = {
            'loadBalancerId': lbid
        }

        ret = self.postRequest(module, region, action, action_params)
        return ret

    def lb_query(self, region, vip, lip):
        '''
        查询负载均衡
        :param region: 
        :param vip: 
        :param lip: 
        :return: 
        '''
        module = 'lb'
        action = 'DescribeLoadBalancers'

        # 接口参数
        action_params = {}
        if vip:
            action_params['loadBalancerVips.0'] = vip
        if lip:
            action_params['backendLanIps.0'] = lip

        ret = self.postRequest(module, region, action, action_params)
        return ret

    def lb_backend_modify(self, region, lbid, bid_list, weight):
        '''
        变更后端机器权重
        :param region: 区域，默认广州
        :param lbid: 负载均衡ID
        :param bid_list: 云主机ID列表
        :param weight: 权重
        :return: 
        '''
        module = 'lb'
        action = 'ModifyLoadBalancerBackends'

        # 接口参数
        action_params = {
            'loadBalancerId': lbid,
        }
        for i in range(0, len(bid_list)):
            action_params['backends.%s.instanceId' % i] = bid_list[i]
            action_params['backends.%s.weight' % i] = int(weight)

        ret = self.postRequest(module, region, action, action_params)
        return ret


if __name__ == '__main__':
    qapi = QcloudSDK(secretid='******', secretkey='******')
    # r = qapi.lb_list('')
