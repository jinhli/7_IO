#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/26/18


from os import getcwd
import os
from sys import path as sys_path
import re
import socket
import subprocess
import struct
import json
import hashlib
import configparser
from conf import setting
from core.md5_server import get_md5
from core import logger
from core import Mythread
from threading import Thread, current_thread
import threading

sys_path.insert(0, os.path.dirname(getcwd()))
access_log = logger.logger('auth')
upload_log = logger.logger('put')
download_log = logger.logger('get')


class Ftp_server:

    STATUS_CODE ={
        200: 'Account authentication',
        201: 'Wrong username or password',
        301: 'File does not exist',
        300: 'File exists',
        302: 'The directory is empty',
        303: 'The directory does not exist',
        400: 'Upload successfully',
        401: 'Upload file failed',
        500: 'MD5 check successfully',
        501: 'MD5 check failed',
        600: 'The space  is enough',
        601: 'There is no enough space'


    }

    def __init__(self, management_instance):
        self.management_instance = management_instance
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((setting.ADDR, setting.PORT))
        self.server.listen(setting.MAX_SOCKET_LISTEN)
        self.pool = Mythread.MyThread(setting.MAX_WORKERS)

        self.accounts = self.load_accouts()
        self.user_info = {}  # 初始化字典


    def start_server(self):
        """
        启动ftp server
        :return:
        """

        print('start ftp server on %s:%s'.center(50, '-') % (setting.ADDR, setting.PORT))
        while True:
            conn, addr = self.server.accept()
            print('got a new connection from %s......' % (addr,))
            t = self.pool.get_thread()   #
            obj = t(target=self.handle, args=(conn, addr,))
            obj.start()



    def stop_server(self, conn):
        print('stop ftp server')
        conn.close()
        self.server.close()
    #
    # def restart_server(self):
    #     self.stop_server()
    #     self.start_server()

    def handle(self, conn, addr):
        """
        处理与用户的所有指令交互
        :return:
        """

        while True:
            print('线程名--》%s' % threading.current_thread().getName())

            data = self.recv_header(conn)  # 传过来的数据

            if not data:
                username = self.user_info[current_thread().name][3]
                print('connection %s is lost ....' % (addr,))
                access_log.info('%s has logout ' % username)
                del addr
                self.pool.put_thread()  # 释放线程到线程池
                break
            else:
                action_type = data.get('action_type')
                if action_type:
                    if hasattr(self, '_%s' % action_type):
                        func = getattr(self, '_%s' % action_type)
                        func(conn, data, *(current_thread().name, conn))
                        continue
                else:
                    print('invalid command')

    def send_message(self, conn, status_code,  *args, **kwargs):  # 报头发布信息，防止粘包
        """
        发送报头
        :param kwargs: 字典
        :return:
        """

        header_dic = kwargs
        header_dic['status_code'] = status_code
        header_dic['status_msg'] = self.STATUS_CODE[status_code]
        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')
        conn.send(struct.pack('i', len(header_bytes)))  # 发一个报头长度
        conn.send(header_bytes)

    def recv_header(self, conn):
        """
        接收报头，并把报头内容转换成字典
        :return:
        """
        obj = conn.recv(4)

        if obj:
            head_len = struct.unpack('i', obj)[0]
            data = conn.recv(head_len).decode('utf-8')
            header_dict = json.loads(data)
            return header_dict
        else:
            return False

    def load_accouts(self):
        """
        加载所有的账号信息
        :return:
        """
        config = configparser.ConfigParser()  # 实例化一个对象
        config.read(setting.account)  # 打开文件 account.ini，保存了用户信息
        return config  # 获得配置文件实例

    def authenticate(self, username, password, thread_name):
        """
        用户认证方法
        :param username:
        :param password:
        :return:
        """
        if username in self.accounts:
            _password = self.accounts[username]['password']
            md5_obj = hashlib.md5()
            md5_obj.update(password.encode())
            md5_password = md5_obj.hexdigest()
            # print('password', _password, md5_password)
            if md5_password == _password:
                home_dir = self.accounts[username]['home']
                home_dir = os.path.join(setting.HOME_DIR, home_dir)
                current_dir = home_dir
                self.user_info[thread_name] = [home_dir, current_dir, self.accounts[username]['quota'], username]
                print(self.user_info)
                access_log.info('%s has logined successfully' % username)
                return True
            else:
                # msg = 'password is not correct'
                return False
        else:
            # msg = 'there is no the account here'
            return False
        # self.send_message(msg)

    def _auth(self, conn, data, *args):  #
        """
        从account里读取文件内容，并进行验证
        :param name:
        :param password:
        :return:
        """
        thread_name = args[0]

        if self.authenticate(data.get('username'), data.get('password'), thread_name):
            home_dir = self.user_info[thread_name][0]

            # relative_dir = current_dir.replace(home_dir, '/')
            relative_dir = self.user_info[thread_name][1].replace(home_dir, '/')
            self.send_message(conn, 200, current_dir=relative_dir)

        else:
            print('auth fail')
            self.send_message(conn, 201)

    def _get(self, conn, data, *args):
        """
        下载到客户端
        :param data:
        报头
        {
        status_code:
        status_msg:
        md5: md5 checksum
        size: 文件大小
        }
        :return:
        """
        _filename = data.get('filename')
        thread_name = args[0]
        username =  self.user_info[thread_name][3]
        current_dir = self.user_info[thread_name][1]
        filename_path = os.path.join(current_dir, _filename)
        if os.path.exists(filename_path):
            file_md5 = get_md5(filename_path)
            file_size = os.path.getsize(filename_path)
            self.send_message(conn, 300, md5=file_md5, size=file_size, file_path=current_dir)
            #  把文件大小，文件绝对路径，传给客户端，保存
            with open(filename_path, 'rb') as f:
                for line in f:
                    conn.send(line)
                else:
                    print('-----file send done------')
                download_log.info('%s has been download successfully by %s' % (_filename, username))

        else:
            self.send_message(conn, 301)

    def _re_get(self, conn, data, *args):
        """
        重新下载文件
        :param data:
        :return:
        """
        file_name = data.get('file_name')
        file_path = data.get('file_path')
        file_size = data.get('file_size')
        send_size = data.get('received_file_size')
        full_path = os.path.join(file_path, file_name)
        thread_name = args[0]
        username =  self.user_info[thread_name][3]

        if os.path.exists(full_path):
            file_md5 = get_md5(full_path)
            if os.path.getsize(full_path) == file_size:
                self.send_message(conn, 300, md5=file_md5, size=file_size)
                f = open(full_path, 'rb')
                f.seek(send_size)
                for line in f:
                    conn.send(line)
                else:
                    print('----file re-send-done-----')
                    f.close()
                    download_log.info('%s has been download successfully by %s' % (file_name, username))
        else:
            self.send_message(conn, 301)

    def _put(self, conn, data, *args):
        """
              从客户端上传文件
              :return: MD5
              """
        _filename = data.get('filename')
        thread_name = args[0]
        current_dir = self.user_info[thread_name][1]
        home_dir = self.user_info[thread_name][0]
        quota = self.user_info[thread_name][2]
        # print('put home_dir %s , qutota %s -->' % (home_dir, quota))
        filename_path = os.path.join(current_dir, _filename)
        _size = data.get('size')
        _md5 = data.get('md5')
        balance_size = self.verify_quota(home_dir, quota)  # 返回家目录剩余空间
        # print('balance_size -->%s' % type(balance_size))
        if balance_size > _size:  # 与上传的文件作对比，如果大，则返回状态码600,可以上传
            self.send_message(conn, 600, balance_size=balance_size)
            if os.path.exists(filename_path):
                filename2 = filename_path + '.bak'
                new_filename = filename2
            else:
                new_filename = filename_path
            self.write_file(conn, new_filename, _size)  # 文件写到服务器home目录下
            self.verify_md5(conn, new_filename, _md5)
            upload_log.info('%s has been upload successfully by %s' % (_filename, thread_name))
        else:
            self.send_message(conn, 601, balance_size=balance_size)

    def _ls(self, conn, data, *args):
        """
        self.accounts.get(self.name, 'home') 这个得到的是账号的家目录
        :return:
        """
        # full_path = path.join(setting.HOME_DIR, current_dir)
        thread_name = args[0]
        print('ls thread_name -->%s ' % thread_name)
        current_dir = self.user_info[thread_name][1]
        print('ls curretn_dir--> %s' % current_dir)
        cmd = 'ls %s' % current_dir  #
        self.handle_cmd(conn, cmd, *args)   # 命令处理函数

    def _cd(self, conn, data, *args):
        """
        目录切换
        只能在家目录内进行切换，可以通过..返回上层目录
        :return:
        """
        thread_name = args[0]
        current_dir = self.user_info[thread_name][1]
        home_dir = self.user_info[thread_name][0]

        target_dir = data.get('target_dir')
        full_path = os.path.join(current_dir, target_dir)
        full_path = os.path.abspath(full_path)   # 取绝对路径是为了 /home/bonnie/../../
        if os.path.isdir(full_path):
            if full_path.startswith(home_dir):  # 当前目录在家目录的范围内
                current_dir = full_path
                relative_dir = current_dir.replace(home_dir, '')
                if relative_dir == '':
                    self.send_message(conn, 300, current_dir='/', size=0)  # 没有命令输出，只在客户端进行目录切换
                else:
                    self.send_message(conn, 300, current_dir=relative_dir, size=0)  # 没有命令输出，只在客户端进行目录切换

            else:
                self.send_message(conn, 303)   # 只能在家目录内切换，否则提示目录不存在

        else:
            self.send_message(conn, 303)  # 提示目录不存在

    def verify_md5(self, conn, file_path, original_md5):
        """
        上传文件MD5 验证
        :param file_path:
        :param original_md5:  # 客户端传过来的MD5
        :return:
        """
        new_md5 = get_md5(file_path)  # 在服务器端文件传完之后生成的md5
        if new_md5 == original_md5:
            self.send_message(conn, 500)  # MD5 检测成功

        else:
            self.send_message(conn, 501)  # MD5 检测失败

    def write_file(self, conn, filename, total_size):
        """
        写文件
        :param filename:
        :return:
        """
        with open(filename, 'wb') as f:
            recv_size = 0
            while recv_size < total_size:
                line = conn.recv(1024)
                f.write(line)
                recv_size += len(line)
            self.send_message(conn, 400)  # 文件上传成功
            print('%s 上传成功' % filename)   #

    def handle_cmd(self, conn, cmd, *args):
        """
        处理系统命令， 比如 ,ls, rm
        :return:
        """
        thread_name = args[0]
        current_dir = self.user_info[thread_name][1]
        home_dir = self.user_info[thread_name][0]
        relative_dir = current_dir.replace(home_dir, '')
        if relative_dir == '':
            relative_dir = '/'
        obj = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = obj.stdout.read()
        stderr = obj.stderr.read()
        data_size = len(stdout) + len(stderr)
        if data_size > 0:
            self.send_message(conn, 300, size=data_size, current_dir=relative_dir)  # 目录不为空，有返回值
            conn.send(stdout)
            conn.send(stderr)
        else:
            self.send_message(conn, 302)  # 目录为空，无返回值

    def verify_quota(self, home_dir, quota):
        """

        :param account_quota:  # 从用户配置文件中获得 如：4G
        :param home_dir:  # 从用户配置文件中获得， 绝对路径
        /home/bonnie/python_learning/pycharm_project/6_socket/socket_homework/ftp_并发/server/home/bonnie
        :return: # 返回家目录剩余空间
        """

        # print('verify_quota excute')
        # thread_name = args[0]
        # current_dir = self.user_info[thread_name][1]
        # home_dir = self.user_info[thread_name][0]
        # quota = self.user_info[thread_name][2]

        # print('quota home_dir %s, qutota %s -->' %(home_dir, quota))
        
        _size = re.match('\d+', quota).group()  # 配额数字
        _unit = re.search('\w$', quota).group()  # 配额单位， M， G
        if _unit == 'M':
            real_size = float(_size)*1024.0*1024.0  # 换算成B
        else:
            real_size = float(_size)*1024.0*1024.0*1024.0  # 换算成B

        if os.listdir(home_dir):

            for dirname in os.listdir(home_dir):  # 获取二级目录所有文件夹与文件
                Dir = os.path.join(home_dir, dirname)  # 路径补齐
                count = 0
                if os.path.isfile(Dir):  # 判断是根目录下是否有文件
                    size = os.path.getsize(os.path.join(home_dir, dirname))
                    count += size
                else:  # 判断是否为目录
                    for r, ds, files in os.walk(Dir):  # 遍历目录下所有文件根，
                        # 目录下的每一个文件夹(包含它自己), 产生3-元组 (dirpath, dirnames, filenames)【文件夹路径, 文件夹名字, 文件名称】
                        for file in files:  # 遍历所有文件
                            size = os.path.getsize(os.path.join(r, file))  # 获取文件大小
                            count += size
                balance_size = real_size - count
                if balance_size > 0:
                    return balance_size
        else:
            balance_size = real_size
            return balance_size





