#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/22/18

from multiprocessing import Process, JoinableQueue
import time, random, os


def consumer(q, name):
    while True:
        res = q.get()
        time.sleep(random.randint(1,3))
        print('\033[43m%s 吃 %s\033[0m' % (name, res))
        q.task_done()


def producer(q, name, food):
    for i in range(3):
        time.sleep(random.randint(1,3))
        res='%s%s' % (food, i)
        q.put(res)
        print('\033[45m%s 生产了 %s\033[0m' %(name,res))
    q.join()  # 等到消费者把自己放入队列中所有的数据都取走之后，生产者才结束


if __name__ == '__main__':
    q = JoinableQueue()
    # 生产者们:即厨师们
    p1=Process(target=producer, args=(q, 'egon', '包子'))

    # 消费者们:即吃货们
    c1=Process(target=consumer, args=(q, 'alex'))
    c1.daemon = True

    # 开始
    p1.start()
    c1.start()
    p1.join()
    print('主')