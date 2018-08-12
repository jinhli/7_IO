#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/21/18
#
# from socket import *
# from concurrent.futures import ThreadPoolExecutor
#
#
# def communicate(conn):
#     while True:
#         try:
#             data = conn.recv(1024)
#             if not data:break
#             conn.send(data.upper())
#         except ConnectionError:
#             break
#
# def server(ip,port):
#     server = socket(AF_INET, SOCK_STREAM)
#     server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#     server.bind((ip, port))
#     server.listen(5)
#
#     while True:
#         conn, addr = server.accept()
#         pool.submit(communicate, conn)
#
#
#
# if __name__== '__main__':
#     pool =  ThreadPoolExecutor(2)
#     server('127.0.0.1', 8081)


from socket import *
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, currentThread
import threading
import queue

ADDR='127.0.0.1'
PORT=8085
MAX_SOCKET_LISTEN = 5
MAX_WORKERS = 5

class MyThread():
    """
        自定义的线程类，使用queue支持简单的线程池
    """
    def __init__(self,maxsize):
        """
        :param maxsize:  队列的数量
        """
        self.maxsize = maxsize
        self.q = queue.Queue(maxsize)  # 初始化一个队列对象
        # 在队列中先存放maxsize个队列对象。这一步就做到了线程池的作用。
        for i in range(maxsize):
            self.q.put(threading.Thread)  # 在队列中先存放线程对象

    def get_thread(self):
        """  从队列中拿取线程对象
        :return:
        """
        return self.q.get()

    def put_thread(self):
        """  往队列中存放线程对象
        :return:
        """
        self.q.put(threading.Thread)


class Ftp_server:

    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind((ADDR, PORT))
        self.server.listen(MAX_SOCKET_LISTEN)
        self.pool = MyThread(MAX_WORKERS)

    def communicate(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print('no data, break')
                    break
                else:
                    conn.send(data.upper())
                    self.pool.put_thread()
                    continue
            except ConnectionError:
                break

    def start_server(self):
        while True:
            conn, addr = self.server.accept()
            print('got a new connection from %s......' % (addr,))
            t = self.pool.get_thread()  #
            obj = t(target=self.communicate, args=(conn,))
            obj.start()


if __name__== '__main__':

    ftp_server = Ftp_server()
    ftp_server.start_server()

