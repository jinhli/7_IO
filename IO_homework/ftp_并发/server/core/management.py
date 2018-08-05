#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/29/18

from os import path, getcwd
from sys import path as sys_path
sys_path.insert(0,path.dirname(getcwd()))
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

from core.Ftp_server import Ftp_server


class Management:
    """

    """
    def __init__(self,sys_argv):
        self.sys_argv = sys_argv
        print(self.sys_argv)

    def verify_arg(self):
        """

        :return:
        """
        if len(self.sys_argv) < 2:
            self.help_msg()
        cmd = self.sys_argv[1]
        if not hasattr(self, cmd):
            print('invalid parameters')
            self.help_msg()

    def help_msg(self):
        msg = """
        start   start ftp server
        stop    stop ftp server
        restart restart ftp server
        create  username  create a ftp server
        
        """
        print(msg)

    def execute(self):
        cmd = self.sys_argv[1]
        func = getattr(self, cmd)
        func()

    def start(self):
        """
        启动服务器
        :return:
        """
        server = Ftp_server(self) # 服务器的实例和管理组合
        server.start_server()

    def createuser(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass


    def deluser(self):
        pass



