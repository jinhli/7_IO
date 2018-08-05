#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 7/6/18


import logging
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  #整个程序的主目录
sys.path.append(BASE_DIR)
from conf.setting import *


def logger(log_type):

    logger = logging.getLogger(log_type)
    logger.setLevel(LOG_LEVEL)
    log_file = '%s/log/%s' %(BASE_DIR, LOG_TYPES[log_type])

    fh = logging.FileHandler(log_file)
    fh.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')

    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


# access = logger('auth')
# access.info('I am here')