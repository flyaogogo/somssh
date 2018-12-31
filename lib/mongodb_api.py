#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: mongo_api.py
# @Time: 18-1-23 下午6:36

import time

from pymongo import MongoClient, ASCENDING

from lib.common import get_dir


class GetSysData(object):

    def __init__(self, monitor_item, timing, collection, no=0):
        self.collection = collection
        self.monitor_item = monitor_item
        self.timing = timing
        self.no = no

    @classmethod
    def connect_db(cls):
        mongodb_ip = get_dir("mongodb_ip")
        mongodb_port = get_dir("mongodb_port")
        mongodb_user = get_dir("mongodb_user")
        mongodb_pwd = get_dir("mongodb_pwd")
        if mongodb_user:
            uri = 'mongodb://'+mongodb_user+':'+mongodb_pwd+'@'+mongodb_ip+':'+mongodb_port+'/'+cls.collection
            client = MongoClient(uri)
        else:
            client = MongoClient(mongodb_ip, int(mongodb_port))
        return client

    def get_data(self, filter, exclude):
        client = self.connect_db()
        db = client["somsshdb"]
        if not self.collection:
            collection = db[get_dir("mongodb_collection")]
        else:
            collection = db[self.collection]
        now_time = int(time.time())
        find_time = now_time-self.timing
        cursor = collection.find(filter, exclude).sort('log_time', -1).limit(self.no)
        return cursor

    def insert_data(self, data):
        client = self.connect_db()
        db = client["somsshdb"]
        if not self.collection:
            collection = db[get_dir("mongodb_collection")]
        else:
            collection = db[self.collection]
        cursor = collection.insert_one(data)
        return cursor

    def multi_insert_data(self, data):
        client = self.connect_db()
        db = client["somsshdb"]
        if not self.collection:
            collection = db[get_dir("mongodb_collection")]
        else:
            collection = db[self.collection]
        cursor = collection.insert_many(data)
        return cursor

