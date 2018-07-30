#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/29/18


# 基于yield并发执行
import time


def consumer():
    '''任务1:接收数据,处理数据'''
    while True:
        x = yield
        print(x)


def producer():
    '''任务2:生产数据'''
    g=consumer()
    next(g)
    for i in range(10000000):
        g.send(i)
        print(i)

start=time.time()
producer()
stop=time.time()
print(stop-start)