# -*- coding: utf-8 -*-
# @Time : 2021/4/21 13:03
# @Author : *
# @Site :
# @File : testAlarm.py
# @Software: PyCharm
import logging
import os
import signal
import subprocess
from time import sleep


#logging.config.fileConfig('log.conf')
#logger = logging.getLogger('APKTestEngine')


pid1 = os.getpid()
print("father pid: %s" % pid1)
sleep(10)
sub = subprocess.Popen(["python3", "testAlarm2.py"], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
pid2 = sub.pid
print("child1 pid %s" % pid2)
#os.system("python3 testAlarm2.py")
#testAlarm2.fun()
#result = sub.wait(30)
#print(result)
#out = sub.stdout.readlines()
#print(out)
#logger.debug("prepareing signal send")
sleep(60)
sub.send_signal(signal.SIGINT)
print("send ok")
sleep(60)
#logger.debug("signal send")
