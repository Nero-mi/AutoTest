#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import paramiko
from sdk.log import log
from stat import S_ISDIR as isdir


PyPath = os.getcwd()#获取当前路径
ShellLocal = time.localtime()#打印实时时间

Command = ['<Micmega>','#','$']


class Linux():

    def __init__(self, hostname, port, username, password, timeout=30):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        
        ## Transport：是一种加密的会话，使用时会同步创建了一个加密的Tunnels(通道)，这个Tunnels叫做Channel
        ## Channel：是一种类Socket，一种安全的SSH传输通道
        ## Session：是client与Server保持连接的对象，用connect()/start_client()/start_server()开始会话
        self.t = ""
        self.chan = ""
        # self.t_sftp = ""
        self.SFTPClient = ""
        

        ## 连接失败重试的次数
        self.try_times = 100


        """
        ansi字符转义,在Shell返回值中会出现特殊字符无法简单进行转义,其为term上显示彩色,需要用正则表达式处理
            \x1B  # ESC
            (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
            |     # or [ for CSI, followed by a control sequence
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        """
        self.ansi_transform = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        

    def connect(self):
        while True:

            ## 连接过程中可能会抛出异常，比如网络不通，或者连接超时
            try:
                self.t = paramiko.Transport(sock=(self.hostname, self.port))
                self.t.connect(username=self.username, password=self.password)
                self.chan = self.t.open_session() ## 获取一个通道
                self.chan.settimeout(self.timeout)
                self.chan.get_pty() ## 激活通道
                self.chan.invoke_shell()
                # self.SFTPClient = paramiko.SFTPClient.from_transport(self.t)

                
                # 连接ssh成功打印字符串
                time.sleep(1)
                
                # print('SSH Connect %s success!'%(self.hostname))
                ret = self.chan.recv(65535).decode('utf-8')#拿到打印结果换成utf-8格式
                # print(ret)
                

                # # 连接sftp成功打印字符串
                # self.t_sftp = paramiko.Transport((self.hostname, self.port))
                # self.t_sftp.connect(username=self.username, password=self.password)
                # self.SFTPClient = paramiko.SFTPClient.from_transport(self.t_sftp)
                # # print('SFTPClient Connect %s success!\n'%(self.hostname))
                # log.info('SFTPClient Connect %s success!\n'%(self.hostname))

                return ret
            

            except Exception:
                if self.try_times != 0:
                    # print('Connect %s fail, reconnect! %s time'%(self.hostname,self.try_times))
                    log.warning('Connect %s fail, reconnect! %s time'%(self.hostname,self.try_times))
                    # time.sleep(3)
                    self.try_times -= 1
                 

                else:
                    # print('Reconnect 100 times fail, end connect!!!')
                    log.error('Reconnect %d times fail, end connect!!!' %(self.try_times))
                    sys.exit(1)

                    #exit(1) ## 异常退出
                    return "SSH Connect Failed"

    def command_status(self, timeout = 60):
        interval = 0.1
        count = 0
        while True:
            if  count > (timeout / interval):                               # 判断命令执行时间时间超过上限，默认60S
                break
            time.sleep(interval)
            if self.chan.exit_status_ready():                               # 命令已经结束，获取退出状态
                exit_status = self.chan.recv_exit_status()
                # print("Command exit stauts: %d" %exit_status)
                log.info("Command exit stauts: %d" %exit_status)
                return True
            elif self.chan.closed:                                          # 通道已关闭，但退出状态尚未准备好
                # print("Channel bas been closed")
                log.error("Channel bas been closed")
                sys.exit(1)
                break
            count = count + 1                                           
        return False
    

    def exec_command(self,cmd):
        ansi_escape = self.ansi_transform
        cmd += '\r'
        result = ''
        # result = cmd
        self.chan.send(cmd)
        ## 回显很长的命令可能执行的比较久，通过循环分批次取回回显
        if self.command_status(self):
            if self.chan.recv_ready() == True:
                ret = self.chan.recv(1024)
                try:
                    ret = ret.decode('utf-8', 'ignore')#ignore防止换格式发生错误
                except UnicodeDecodeError as e:
                    log.error(ret+e)
                    sys.exit(1)
                ret = ansi_escape.sub('', ret)
                # print(ret)
                result += ret
                return result
                # if result[-8:-1] == "Micmega" or (result[-2] == "#") or (result[-2] == "$"):           # "Micmega" 命令提示符作为命令完成的标志
                #     return result
    

    def send_recv_upgrade(self,cmd):
        ansi_escape = self.ansi_transform
        result = ''
        cmd += '\r'
        self.chan.send(cmd)
        time.sleep(10)

        while True:
            if self.chan.recv_ready() == True:
                ret = self.chan.recv(1024)
                ret = ret.decode('utf-8')
                ret = ansi_escape.sub('', ret)
                # print(ret)
                result += ret
                if("Start to upgrade above firmwares? Please input Y/N") in result:
                    if "error" in result or "fail" in result:
                        log.error("FTP Download Firmware Failed!")
                        self.chan.send('n\r')
                        time.sleep(3)
                        ret = self.chan.recv(1024)
                        ret = ret.decode('utf-8')
                        ret = ansi_escape.sub('', ret)
                        # print(ret)
                        result += ret
                        sys.exit(1)
                        return result
                    else:
                        # print(result)
                        self.chan.send('y\r')
                        break
            else:
                time.sleep(3)

        while True:
            if self.chan.recv_ready() == True:
                ret = self.chan.recv(1024)
                ret = ret.decode('utf-8')
                ret = ansi_escape.sub('', ret)
                # print(ret)
                result += ret
                if (result[-8:-1] in Command) or (result[-2] in Command):           # "Micmega"、"#"、"$" 命令提示符作为命令完成的标志
                    return result
            else:
                time.sleep(3)


    def send_recv(self, cmd, timeout = 60):
        ansi_escape = self.ansi_transform
        cmd += '\r'
        result = ''
        # result = cmd
        self.chan.send(cmd)
        waittime = 0
        ## 回显很长的命令可能执行的比较久，通过循环分批次取回回显
        while True and waittime < timeout:
            if self.chan.recv_ready() == True:
                ret = self.chan.recv(1024)
                try:
                    ret = ret.decode('utf-8', 'ignore')#ignore防止换格式发生错误
                except UnicodeDecodeError as e:
                    log.error(ret+e)
                    continue
                ret = ansi_escape.sub('', ret)
                # print(ret)
                result += ret
                if (result[-9:] in Command) or (result[-2] in Command):           # "Micmega"、"#"、"$" 命令提示符作为命令完成的标志
                    return result
            else:
                time.sleep(3)
                waittime += 1
        log.error("Command [%s] Exec Fail! Please Check Log!" %cmd)


    def close(self):
        self.chan.close()
        self.t.close()
        # self.SFTPClient.close()
        # print('SSH Closed!')
        # log.info('SSH Closed!')
        # print('SFTP Closed!\n')


    def sftp_get_floder(self, remote_dir_name, local_dir_name):
        ## 远程下载文件
        remote_file = self.SFTPClient.stat(remote_dir_name)
        if isdir(remote_file.st_mode):
            # 文件夹，不能直接下载，需要继续循环
            self.check_local_dir(local_dir_name)
            # print('start download floder:' + remote_dir_name)
            log.info('start download floder:' + remote_dir_name)
            for remote_file_name in self.SFTPClient.listdir(remote_dir_name):
                sub_remote = os.path.join(remote_dir_name, remote_file_name)
                sub_remote = sub_remote.replace('\\', '/')
                sub_local = os.path.join(local_dir_name, remote_file_name)
                sub_local = sub_local.replace('\\', '/')
                self.sftp_get_floder(sub_remote, sub_local)
        else:
            # 文件，直接下载
            # print('start download log:' + remote_dir_name)
            log.info('start download log:' + remote_dir_name)
            self.SFTPClient.get(remote_dir_name, local_dir_name)
                     

    def check_local_dir(self, local_dir_name):
        ## 本地文件夹是否存在，不存在则创建
        if not os.path.exists(local_dir_name):
            os.makedirs(local_dir_name)


    def get_all_files_in_local_dir(self, local_dir_name):    # 递归获取本地目录中文件
        all_files = []
        files = os.listdir(local_dir_name)
        for file in files:
            # 统一路径分隔符
            filename = os.path.join(local_dir_name,file).replace("\\","/")
            all_files.append(filename)
        return all_files


    def sftp_put_folder(self, local_dir_name, remote_dir_name):  
        #规范路径名称
        # print(remote_dir_name)
        # print(local_dir_name)
        # if remote_dir_name[-1] != '/':
        #     remote_dir_name = remote_dir_name + '/'
        # print(remote_dir_name[-1])
        ## 获取要上传的文件
        all_files = self.get_all_files_in_local_dir(local_dir_name)
        
        for file in all_files:
            ## 替换文件路径
            # print(file)
            remote_filename = file.replace(local_dir_name, remote_dir_name)
            # print(local_dir_name,remote_dir_name)
            # print(remote_filename)
            # print(self.SFTPClient)
            self.SFTPClient.put(file, remote_filename)