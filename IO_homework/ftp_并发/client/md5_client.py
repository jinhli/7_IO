#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/24/18


import hashlib

import os



def get_md5(file_path):
    md5 = None
    if os.path.isfile(file_path):
        with open(file_path,'rb') as f:
            md5_obj= hashlib.md5()
            md5_obj.update(f.read())
            hash_code = md5_obj.hexdigest()
            md5 = str(hash_code).lower()

    return md5

def verify_md5(file_path, original_md5):
    new_md5 = get_md5(file_path)
    if new_md5 == original_md5:
        print('The file you download is the same as it in the server')
    else:
        print('The file has been changed during the trasfer')


