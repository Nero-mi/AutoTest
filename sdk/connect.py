import time
from sdk.session import Linux
from sdk.log import log
class Connect():
    def __init__(self,hostname, port, username, password, type):
        self.ssh = Linux(hostname, port, username, password)
        self.type = type

    def ssh_connect(self):
        resultStr = self.ssh.connect()
        log.info('SSH Connect %s success!'%(self.ssh.hostname))
        time.sleep(1)
        return resultStr


    def reboot(self):
        cmd = "reboot"
        resultStr = self.ssh.send_recv(cmd)
        log.info('Board Reboot')
        time.sleep(1)
        return resultStr


    def upgrade(self):
        if(self.type == "Debug"): cmd = "upgrade.py all -ip 172.16.128.100"
        else: cmd = "upgrade all -ip 172.16.128.100"
        resultStr = self.ssh.send_recv_upgrade(cmd)
        log.info('Upgrade Done')
        time.sleep(1)
        return resultStr


    def dev_version(self):
        if(self.type == "Debug"): cmd = "version.py"
        else: cmd = "display version"
        resultStr = self.ssh.send_recv(cmd)   
        log.info('Display Version Success')
        time.sleep(1)
        return resultStr


    def ssh_disconnect(self):
        self.ssh.close()
        log.info('SSH Disconnect %s success!'%(self.ssh.hostname))
        time.sleep(1)