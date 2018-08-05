#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 8/2/18



from threading import Thread
import time

def foo():
    print(123)
    time.sleep(1)
    print("end123")

def bar():
    print(456)
    time.sleep(3)
    print("end456")

if __name__ == '__main__':
    t1=Thread(target=foo)
    t2=Thread(target=bar)

    # t1.daemon=True
    t2.daemon=True  # sleep 时间长， 主线程结束，守护线程也结束
    t1.start()
    t2.start()
    print("main-------")