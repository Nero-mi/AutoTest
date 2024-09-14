import logging
import os
import datetime
from logging import Logger, handlers



# 生成测试日志 
PyPath        = os.getcwd()                             # 获取当前项目路径
current_time  = datetime.datetime.now()                 # 获取当前时间
format_time   = current_time.strftime("%Y_%m_%d")       # 格式化时间  Year_Month_Day
Warning_Log   = "Warning_" + format_time                # Log File Name
Debug_Log     = "Debug_" + format_time
log_path      = os.path.join(PyPath,"log")              # 获取日志路径
LogFilePath   = os.path.join(log_path,format_time)     
print(LogFilePath)
if not os.path.exists(LogFilePath):
    os.mkdir(LogFilePath)                               # 新建测试日志路径文件夹
Warning_Log_Path_File = os.path.join(LogFilePath,Warning_Log + ".log")
Debug_Log_Path_File   = os.path.join(LogFilePath,Debug_Log + ".log")


class MyLogger(Logger):

    def __init__(self):

        # 设置日志的名字、日志的收集级别
        super().__init__("test_api", logging.DEBUG)

        # 自定义日志格式(Formatter), 实例化一个日志格式类
        fmt_str = '[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(message)s]'
        date_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt_str,date_fmt)


        # 实例化控制台渠道(StreamHandle)
        console_hl = logging.StreamHandler()
        # 设置控制台输出的日志级别
        console_hl.setLevel(logging.DEBUG)
        # 设置渠道当中的日志显示格式
        console_hl.setFormatter(formatter)
        # 将渠道与日志收集器绑定起来
        self.addHandler(console_hl)

        # # 实例化文件渠道(FileHandle):wq
        # file_hl = logging.FileHandler(log_path_file, mode='a', encoding="utf-8")

        '''
        创建一个文件实例，如果 api_test.log 文件不存在，就会自动创建；
        mode 参数设置为追加；另外为防止乱码， encoding 参数设置为 utf-8 编码格式
        '''
        file_hl = handlers.RotatingFileHandler(Debug_Log_Path_File, maxBytes=10**6, backupCount=5,
                                               encoding="utf-8", mode="a")

        # 设置向文件输出的日志格式
        file_hl.setLevel(logging.DEBUG)
        # 设置渠道当中的日志显示格式
        file_hl.setFormatter(formatter)
        # 加载文件实例到 logger 对象中
        self.addHandler(file_hl)


        # 当log达到最大字节长度，将自动backup5个log文件。当5个log文件都达到最大长度时，将只保留最新的log。
        file_hl1 = handlers.RotatingFileHandler(Warning_Log_Path_File, maxBytes=10 ** 6, backupCount=5,
                                          encoding="utf-8", mode="a")
        # 设置向文件输出的日志格式
        file_hl1.setLevel(logging.WARNING)
        # 设置渠道当中的日志显示格式
        file_hl1.setFormatter(formatter)
        # 加载文件实例到 logger 对象中
        self.addHandler(file_hl1)

        file_hl.close()
        file_hl1.close()
        console_hl.close()


# 实例化MyLogger对象，在其他文件直接使用log就能调用
log = MyLogger()

