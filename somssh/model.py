#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: qitan
# @Email: qqing_lai@hotmail.com
# @Site: https://imaojia.com
# @File: model.py
# @Time: 18-4-25 下午1:11


from mongoengine import *


class TestModel(Document):
    test_key = StringField(required=True)
    test_value = StringField(max_length=50)
