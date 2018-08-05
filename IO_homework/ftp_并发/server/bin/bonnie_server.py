#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/23/18

import os, sys
sys.path.insert(0, os.path.dirname(os.getcwd()))


if __name__ == '__main__':
    from core.management import Management

    argv_parser = Management(sys.argv)
    argv_parser.execute()

