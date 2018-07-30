#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 5/26/18

from multiprocessing import Process
import time
import random

# 创建并开启子进程的方式一

# def piao(name):
#     print('%s piaoing' % name)
#     time.sleep(random.randrange(1, 5))
#     print('%s piao end ' % name)
#
#
# if __name__== '__main__':
#
#     p1 = Process(target=piao, args=('alex',))
#     p2 = Process(target=piao, args=('egon',))
#     p3 = Process(target=piao, args=('bonnie',))
#
#     p1.start()
#     p2.start()
#     p3.start()
#     print('zhu')


# 创建并开启子进程的方式二
#
# class Piao(Process):
#     def __init__(self, name):
#         super().__init__()
#         self.name = name
#
#     def run(self):
#         print('%s piaoing' % self.name)
#         time.sleep(random.randrange(1,5))
#         print('%s piao end' % self.name)
#
#
#
# if __name__== '__main__':
#
#     p1 = Piao('alex')
#     p2 = Piao('egon')
#     p3 = Piao('bonnie')
#
#     p1.start()
#     p2.start()
#     p3.start()
#     print('zhu')

n = 100


def work():
    global n
    n=0
    print('子进程内: ',n)


if __name__ == '__main__':
    p=Process(target=work)
    p.start()
    print('主进程内: ',n)