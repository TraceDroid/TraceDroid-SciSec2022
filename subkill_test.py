import os
import signal
import subprocess
import time
import uiautomator2 as u2

device = u2.connect('8BSX1EQGX')
captureCommand = 'python3 tcs.py -U -f com.outfit7.mytalkingtom2.qihoo -v -p tom2.pcap'
sub = subprocess.Popen(captureCommand, shell = True, bufsize = -1, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
pid = sub.pid
print(pid)

time.sleep(60)

try:
    os.kill(pid, signal.SIGINT)
    os.kill(pid, signal.SIGTERM)
    sub.kill()
except:
    pass

#killCommand = 'kill -2 %s' % pid
#os.system(killCommand)
print('%s killed'% pid)

device.app_stop('com.outfit7.mytalkingtom2.qihoo')
print('app stoped')
