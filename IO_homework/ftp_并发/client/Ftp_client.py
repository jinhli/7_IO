#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Bonnie Li"
# Email: bonnie922713@126.com
# Date: 6/26/18



import os
from sys import path as sys_path
sys_path.insert(0,os.path.dirname(os.getcwd()))
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #整个程序的主目录
HOME_DIR = r'%s/home/' % BASE_DIR
import socket
import struct
import json
import optparse
import shelve
from client.md5_client import *



""""
python ftp_client -h ip -P 8080 """ # 运行格式


class Ftp_client:
    def __init__(self):
        parse = optparse.OptionParser()
        parse.add_option('-s', '--server', dest='server', help='ftp server ip_addr')
        parse.add_option('-P', '--port', type='int', dest='port', help='ftp server port')
        parse.add_option('-u', '--username', dest='username', help='username info')
        parse.add_option('-p', '--password', dest='password', help='password')
        self.options, self.args = parse.parse_args()
        # print(self.options,self.args)
        self.username = None
        self.current_dir = None

    def argv_verification(self):
        if not self.options.server or not self.options.port:
            exit('Error: must supply server and port parameters')

    def make_connection(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.options.server, self.options.port))

    def auth(self):
        count = 0
        while count < 3:
            username = input('username:').strip()
            if not username:continue
            password = input('password:').strip()
            # cmd = {
            #      'action_type': 'auth',
            #      'username': username,
            #      'password': password
            #  }
            self.send_header(username=username, password=password, action_type='auth')
            response = self.recv_message()
            if response.get('status_code') == 200:
                self.username = username
                self.current_dir = response.get('current_dir')

                return True
            else:
                print(response.get('status_msg'))
                count += 1

    def unfinished_file_check(self):
        """
        检查 下载中断的文件
        :return:
        """
        download_history = '%s.download_history' % self.username
        shelve_obj = shelve.open(download_history)
        if list(shelve_obj.keys()):
            print('-------------------Unfinished file list---------------')
            # for key in self.shelve_obj.keys():
            #     print(key)
            #     print(self.shelve_obj[key])

            for index, key in enumerate(shelve_obj.keys()):
                file_path = os.path.join(HOME_DIR, key)  # 下载中段文件的路径
                received_file_size = os.path.getsize(file_path)  # 获取文件已下载大小
                print("%s.  %s  文件大小%s  已经下载%s" % (index, key, shelve_obj[key]['file_size'], received_file_size))
            while True:
                choice = input('[selected the file index to re-download]>>>>').strip()
                if not choice:continue
                if choice == 'q': break
                if choice .isdigit():
                    choice = int(choice)
                    if 0 <= choice <= index:   # 最后一次的index
                        selected_file = list(shelve_obj.keys())[choice]
                        selected_file_path = os.path.join(HOME_DIR, list(shelve_obj.keys())[choice])
                        have_received_size = os.path.getsize(selected_file_path)   # 这个地方可以优化， 当前客户端所在的目录
                        print('tell server to resend file', selected_file)
                        original_file_name = shelve_obj[selected_file]['file_name']
                        self.send_header('re_get', file_size=shelve_obj[selected_file]['file_size'],
                                         file_path=shelve_obj[selected_file]['file_path'],
                                         file_name=original_file_name,
                                         received_file_size=have_received_size)
                        response = self.recv_message()
                        if response.get('status_code') == 300:  # 接收到状态码 300， 表明文件存在
                            original_file_name = os.path.join(HOME_DIR, original_file_name)
                            self.write_file(response, original_file_name, have_received_size)
                            print('\n')
                            print('file re-get done'.center(50, '-'))
                            del shelve_obj[selected_file]  # 文件下载结束，从shelve 中删除文件下载记录
                            original_md5 = response.get('md5')
                            # home_dir = '%s%s' % (HOME_DIR, filename)  # 绝对路径
                            self.verify_md5(original_file_name, original_md5)


                        else:
                            print(response.get('status_msg'))
        shelve_obj.close()

    def interactive(self):
        """处理与ftpserver的所有交互"""

        if self.auth():
            self.unfinished_file_check()
            while True:
                user_input = input('[%s]>>:' % self.current_dir).strip()
                if not user_input: continue
                cmd_list = user_input.split()
                if cmd_list[0] == 'q':
                    del self.client
                    break
                if hasattr(self, '_%s' % cmd_list[0]):
                    func = getattr(self, '_%s' % cmd_list[0])
                    func(cmd_list[1:])

        else:
            print('auth fail')

    def parameter_check(self,args, min_args=None, max_args=None, exact_args=None ):
        """
        参数合法性检查
        :param args:
        :param min_args:
        :param max_args:
        :param exact_args:
        :return:
        """
        if min_args:
            if len(args) < min_args:
                print('require at least %s parameters but  %s received' %(min_args, len(args)))
                return False
        if max_args:
            if len(args) < max_args:
                print('require at most %s parameters but  %s received' % (min_args, len(args)))
                return False
        if exact_args:
            if exact_args != len(args):
                print('require % parameters but %s received' % (exact_args, len(args)))
                return False
        return True

    def _get(self, cmd_args):
        """
        下载文件到客户端
        :return: MD5
        """
        download_history = '%s.download_history' % self.username
        shelve_obj = shelve.open(download_history)
        # print(self.shelve_obj['2.ape.download'])
        if self.parameter_check(cmd_args, exact_args=1):
            filename = cmd_args[0]
            full_path=os.path.join(HOME_DIR, cmd_args[0])  #
            action_type = 'get'
            self.send_header(action_type, filename=filename,)  # 把要下载的命令和文件发送到服务器
            response = self.recv_message()  # 接收服务器发过来的信息
            if response.get('status_code') == 300:  # 接收到状态码 300， 表明文件存在
                download_info = {
                    'file_size': response.get('size'),   # 文件大小
                    'file_path': response.get('file_path'),  # 服务器端文件的地址
                    'file_name': filename
                }
                file_name = '%s.download' % filename  # 把正在下载的文件加一个后缀
                shelve_obj[file_name] = download_info  # 把正在下载的文件信息保存到文档
                self.write_file(response, full_path, 0)  # ‘0’接受文件大小的初始化
                print('\n')
                print('file get done'.center(50, '-'))
                del shelve_obj[file_name]     # 文件下载结束，从shelve 中删除文件下载记录
                original_md5 = response.get('md5')
                self.verify_md5(full_path, original_md5)
            else:
                print(response.get('status_msg'))
        shelve_obj.close()

    def _put(self, cmd_args):
        """
        上传文件到客户端
        :return:
        """

        if self.parameter_check(cmd_args, exact_args=1):
            action_type = 'put'
            _filename = cmd_args[0]
            filename_path = os.path.join(HOME_DIR, _filename)

            if os.path.exists(filename_path):   # 扩展 如果输入的是个绝对路径，要取出文件名
                file_md5 = get_md5(filename_path)
                file_size = os.path.getsize(filename_path)
                self.send_header(action_type, filename=_filename, md5=file_md5, size=file_size)
                response = self.recv_message()  # 接受配额判断的消息
                if response.get('status_code') == 600:  # 还有剩余空间

                    progress_generator = self.process_bar(file_size)  # 进度条生成器
                    progress_generator.__next__()
                    with open(filename_path, 'rb') as f:
                        send_size = 0
                        for line in f:
                            self.client.send(line)
                            send_size += len(line)  # 发送行
                            progress_generator.send(send_size)  # 调用进度条函数
                    response = self.recv_message()  # 接受上传成功的消息
                    print('\n')
                    if response.get('status_code') == 400:  # 接受状态码400，表示上传成功
                        print(response.get('status_msg'))
                        response = self.recv_message()
                        if response.get('status_code') == 500:  # MD5 检验成功
                            print('MD5 verify successfully on Server')
                        else:
                            print(response.get('status_msg'))

                    else:
                        print(response.get('status_msg'))
                else:
                    print('only %s B space left, no enough space to save the %s' % ('%.2f' % response.get('balance_size'), _filename))

            else:
                print('%s does not exist, please check %s file_path is right' % (_filename, filename_path))

    def _ls(self, cmd_args):
        """
        ls  后面不加参数
        :param cmd_args:
        :return:
        """
        if self.parameter_check(cmd_args, exact_args=0):
            action_type = 'ls'
            self.send_header(action_type)
            response = self.recv_message()  # 接收服务器端返回的消息
            if response.get('status_code') == 302:  # 接受状态码302，当前目录没有文件
                print(response.get('status_msg'))
            else:
                self.print_data(response)  # 接收 目录显示

    def _cd(self, cmd_args):
        """
        cd home  -> cmd_args[0]=home
        :param cmd_args:
        :return:
        """
        if self.parameter_check(cmd_args, exact_args=1):
            action_type = 'cd'
            target_dir = cmd_args[0]
            self.send_header(action_type, target_dir=target_dir)
            response = self.recv_message()  # 接受服务器端返回的消息
            if response.get('status_code') == 300:  # 接受状态码300，显示目录切换成功
                self.current_dir = response.get('current_dir')
                self.print_data(response)  # 显示目录切换
            else:
                print(response.get('status_msg'))  # 打印当前目录不存在

    def send_header(self, action_type, **kwargs):  # 报头发布信息，防止粘包
        """
        发送报头
        :param kwargs: 字典
        :return:
        """
        header_dic = {'action_type': action_type
        }
        header_dic.update(kwargs)
        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')
        self.client.send(struct.pack('i', len(header_bytes)))  # 发一个报头长度
        self.client.send(header_bytes)

    def recv_message(self):
        """
             接收报头，并把报头内容转换成字典
             :return:
             """
        obj = self.client.recv(4)
        head_len = struct.unpack('i', obj)[0]
        data = self.client.recv(head_len).decode('utf-8')
        header_dict = json.loads(data)
        return header_dict

    def write_file(self, header_dict, filename, recv_size):
        """
        下载文件保存
        :param filename:
        :return:
        """

        total_size = header_dict.get('size')
        progress_generator = self.process_bar(total_size)
        progress_generator.__next__()
        filename_1 = '%s.download' % filename
        with open(filename_1, 'ab') as f:     # 可以扩展，确认当前文件是否存在，或者是否覆盖
            while recv_size < total_size:
                line = self.client.recv(1024)
                f.write(line)
                recv_size += len(line)
                progress_generator.send(recv_size)
        os.replace(filename_1, filename)

    def process_bar(self, total_size):
        """
        打印进度条
        :param total_size:
        :return:
        """
        current_percent = 0
        last_percent = 0
        while True:
            recv_size = yield current_percent
            current_percent = int(recv_size / total_size * 100)
            if current_percent > last_percent:
                print('#' * int(current_percent / 2) + '{percent}%'.format(percent=current_percent), end='\r',
                      flush=True)  # \r 作用就是当前行从头覆盖
                last_percent = current_percent

    def print_data(self, header_dict):
        """
        处理收到到数据，主要是命令行返回的数据
        :param header_dict:
        :return:
        """
        # print('调试--》%s' % header_dict)
        total_size = header_dict['size']
        recv_size = 0
        recv_data = b''
        while recv_size < total_size:
            res = self.client.recv(1024)
            recv_data += res
            recv_size += len(res)

        print('[%s]>>:' % header_dict['current_dir'], '\n' + recv_data.decode('utf-8'))   # 优化下 就可以仿照登陆用户的组目录显示 [bonnie@bonnie]>>

    def verify_md5(self, file_path, original_md5):
        """
        上传文件MD5 验证
        :param file_path:
        :param original_md5:  # 客户端传过来的MD5
        :return:
        """
        new_md5 = get_md5(file_path)
        filename = os.path.basename(file_path)
        if new_md5 == original_md5:
            print('md5 check successfully for %s' % filename)  # MD5 检测成功

        else:
            print('md5 check failed for %s' % filename) # MD5 检测失败


if __name__ == '__main__':

    ftp_client = Ftp_client()
    ftp_client.make_connection()
    ftp_client.interactive()



