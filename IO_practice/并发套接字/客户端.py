#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/21/18


from socket import *

client = socket(AF_INET,SOCK_STREAM)
client.connect(('127.0.0.1',8081))

while True:
    msg= input('>>:').strip()
    if not msg: continue
    client.send(msg.encode('utf-8'))
    data = client.recv(1024)
    print(data.decode('utf-8'))

client.close()