#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/24/18


from threading import Thread, Semaphore
import threading
import time
import random


def func():
    with sm:
        print('%s get sm' % threading.current_thread().getName())
        time.sleep(random.randint(1, 3))


if __name__ == '__main__':
    sm = Semaphore(3)
    for i in range(10):
        t = Thread(target=func)
        t.start()







