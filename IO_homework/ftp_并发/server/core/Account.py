#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/29/18


class Account():
    def __init__(self, name, home_dir,quota, status):
        self.name = name
        self.home_dir = home_dir
        self.quota = quota
        self.status = status

