#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/24/18


import hashlib

import os

# file_path =r'/home/bonnie/python_learning/pycharm_project/6_socket/socket_homework/online_ftp/conf/client/lili/1.jpeg'


def get_md5(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            md5_obj = hashlib.md5()
            md5_obj.update(f.read())
            hash_code = md5_obj.hexdigest()
            md5 = str(hash_code).lower()
            print('client md5 is %s' % md5)

    return md5





