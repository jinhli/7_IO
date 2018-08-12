#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/23/18

from os import getcwd, path
from sys import path as sys_path
import logging
sys_path.insert(0, path.dirname(getcwd()))

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__))) #整个程序的主目录

HOME_DIR = path.join(BASE_DIR, 'home')
account = path.join(BASE_DIR, 'conf/account.ini')


ADDR = '127.0.0.1'
PORT = 8080
MAX_SOCKET_LISTEN = 5
MAX_WORKERS = 5

LOG_LEVEL = logging.INFO  #日志的级别
LOG_TYPES = {
             'get': 'download.log',
             'put': 'upload.log',
            'auth': 'access.log'

}

