import os
import time,datetime
import json
from  sdk.connect import Connect


class Board_Test():
    def __init__(self):
        # 获取当前路径
        path = os.getcwd()   
        # 获取json配置文件
        json_file_path = os.path.join(path,'conf') + '/Config.json'
        with open(json_file_path,'r') as file:
            data = json.load(file)

        # 获取配置属性
        self.type = data["Board"]["Type"]
        self.smu = data["Board"]["SMU"]
        self.dru = data["Board"]["DRU"]
        self.port = data["Board"]["Port"]
        self.username = data["Board"]["Username"]
        self.password = data["Board"]["Password"]

        # 生成过程日志 
        PyPath             = os.getcwd()                                      # 获取当前项目路径
        current_time       = datetime.datetime.now()                          # 获取当前时间
        format_time        = current_time.strftime("%Y_%m_%d_%H_%M_%S")       # 格式化时间  Year_Month_Day_Hour_Min_Sec
        format_day         = current_time.strftime("%Y_%m_%d")                # 格式化时间  Year_Month_Day
        Log_File           = "Board_Console_Info_" + format_time              # Log File Name
        log_path           = os.path.join(PyPath,"log")                       # 获取日志路径
        self.LogFilePath   = os.path.join(log_path,format_day,Log_File + ".txt")      

    # 命令行交互信息记录
    def Console_Log(self,Console_info = ""):
        with open(self.LogFilePath, mode="a", encoding="utf-8") as file:
            file.write(Console_info + "\n")


    def Upgrade(self,loop=1):

        for i in range(loop):
            self.Console_Log("================================Upgrade Loop %s Time================================" %i)
            # 连接DRU
            ssh_dru = Connect(self.dru, self.port, self.username, self.password, self.type)
            Console_Connect = Connect.ssh_connect(ssh_dru)
            self.Console_Log(Console_Connect)
            time.sleep(1)

            # # 查看版本
            # Console_Version = Connect.dev_version(ssh_dru)
            # self.Console_Log(Console_Version)
            # time.sleep(1)


            # # 升级
            # Console_Upgrade = Connect.upgrade(ssh_dru)
            # self.Console_Log(Console_Upgrade)
            # time.sleep(3)


            # # 断开连接
            # Connect.ssh_disconnect(ssh_dru)
            # time.sleep(1)


            # # 建立连接 SMU
            # ssh_smu = Connect.Linux(self.smu, self.port, self.username, self.password)
            # Console_Connect = Connect.ssh_connect(ssh_smu)
            # self.Console_Log(Console_Connect)
            # time.sleep(1)


            # # 查看版本
            # Console_Version = Connect.dev_version(ssh_smu)
            # self.Console_Log(Console_Version)
            # time.sleep(1)


            # # 升级
            # Console_Upgrade = Connect.upgrade(ssh_smu)
            # self.Console_Log(Console_Upgrade)
            # time.sleep(3)


            # # 整机断电重启
            # Console_Reboot = Connect.reboot(ssh_smu)
            # self.Console_Log(Console_Reboot)
            # Connect.ssh_disconnect(ssh_smu)
            # time.sleep(120)


            # # 重启后连接 SMU
            # Console_Connect = Connect.ssh_connect(ssh_smu)
            # self.Console_Log(Console_Connect)
            # time.sleep(1)


            # # 查看版本
            # Console_Version = Connect.dev_version(ssh_smu)
            # self.Console_Log(Console_Version)
            # time.sleep(1)


            # # 断开连接
            # Connect.ssh_disconnect(ssh_smu)
            # time.sleep(1)


            # # 重启后连接  DRU
            # Console_Connect = Connect.ssh_connect(ssh_dru)
            # self.Console_Log(Console_Connect)
            # time.sleep(1)


            # 查看版本
            Console_Version = Connect.dev_version(ssh_dru)
            self.Console_Log(Console_Version)
            time.sleep(1)


            # 断开连接
            Connect.ssh_disconnect(ssh_dru)
            time.sleep(1)

        return True
