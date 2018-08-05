#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/24/18

from threading import Thread,Event
import threading
import time, random


def conn_mysql():
    count = 1
    while not event.isSet():  # event.is_set()
        if count > 3:
            raise TimeoutError('链接超时')
        print('<%s>第%s次尝试链接' % (threading.current_thread().getName(), count))
        event.wait(0.5)
        count += 1
        # event.set()
    print('<%s>链接成功' % threading.current_thread().getName())


def check_mysql():
    print('\033[45m[%s]正在检查mysql\033[0m' % threading.current_thread().getName())
    time.sleep(random.randint(2,4))
    while not event.isSet():
        print('连接失败', threading.current_thread().getName())
        event.set()
    # event.set()



if __name__ == '__main__':
    event=Event()
    conn1=Thread(target=conn_mysql)
    conn2=Thread(target=conn_mysql)
    check=Thread(target=check_mysql)

    conn1.start()
    # event.clear()
    conn2.start()
    check.start()

