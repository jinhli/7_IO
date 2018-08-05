#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/22/18

# from threading import Thread
# import time
#
# def sayhi(name):
#     time.sleep(2)
#     print('%s say hello' %name)
#
#
# if __name__=='__main__':
#     t=Thread(target=sayhi,args=('egon',))
#     t.start()
#     t.join()
#     print('驻县城')
#


# from threading import Thread
# import threading
# import os
# import time
# def work():
#     global n
#     n=0
#     time.sleep(3)
#     print(threading.current_thread().getName())
#     print('线程1', n)
#
# if __name__ == '__main__':
#     n=100
#     t=Thread(target=work)
#     t.start()
#     print(threading.current_thread().getName())
#     print(threading.current_thread()) #主线程
#     print(threading.enumerate()) #连同主线程在内有两个运行的线程
#     print(threading.active_count())
#     t.join()
#     # n = 100
#     print(t.is_alive())
#     print('主',n)


