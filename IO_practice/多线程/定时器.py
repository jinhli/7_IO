#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/24/18

# 应用场景 验证码

# from threading import Timer
#
# def hello():
#     print("hello, world")
#
# t = Timer(1, hello)
# t.start()  # after 1 seconds, "hello, world" will be printed
#
# def hello():
#     print("hello, world")
#
# t = Timer(1, hello)
# t.start()  # after 1 seconds, "hello, world" will be printed


import random
from threading import Timer



class Code:

    def __init__(self):
        self.make_cache()

    def make_cache(self, interval=10):
        self.cache = self.make_code()
        print(self.cache)
        self.t = Timer(interval, self.make_cache)
        self.t.start()

    def make_code(self, n=4):

        res= ''
        for i in range(n):
            s1 = str(random.randint(0,9))
            s2 = chr(random.randint(65,90))
            res+= random.choice([s1,s2])
        return res

    def check(self):
         while True:
            code = input('请输入验证码》》：').strip()
            if code.upper()== self.cache:
                print('输入正确')
                self.t.cancel()
                break



obj = Code()
obj.check()

