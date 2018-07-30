#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/21/18

from socket import *
from concurrent.futures import ThreadPoolExecutor


def communicate(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:break
            conn.send(data.upper())
        except ConnectionError:
            break

def server(ip,port):
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        pool.submit(communicate, conn)



if __name__== '__main__':
    pool =  ThreadPoolExecutor(2)
    server('127.0.0.1', 8081)





