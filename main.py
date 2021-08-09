# -*- coding: utf-8 -*-
# @Time :  16:40
# @Author : *
# @Site :
# @File : main.py
# @Software: PyCharm
import configparser
import logging.config
import logging.handlers
import os
import signal
import time
import subprocess

import psutil

import init
import uiautomator2 as u2
import DBUtils

logging.config.fileConfig('log.conf')
logger = logging.getLogger('APKTestEngine')

config = configparser.ConfigParser()
config.read('./config.conf')
deviceConfig = config['device']
fileConfig = config["filePath"]


# device = u2.connect(deviceConfig['deviceID'])

# 进行APP的初始化操作，并将初始化操作日志存入数据库
def preProcessAPK(APK) -> object:
    """

    :param APK，单个APK的元数据信息
    :return:
    """

    logger.info('start preprocessing app')
    logger.info('APK Name: %s; APP Name: %s; APKFilePath: %s', APK["APKName"], APK["APPName"], APK["APKFilePath"])

    # APKFilePath = APK["APKFilePath"]
    return init.verifyPermissions(APK)


def startCapture(APK):
    """

    :param APKID: 单个APK的元数据信息
    :return:
    """
    APKID = APK["APKID"]
    APKName = APK["APKName"]
    packageName = APK["packageName"]
    APPName = APK["APPName"]
    logger.debug('start capture APK traffic')
    logger.debug('APK Name: %s; APP Name: %s', APK["APKName"], APKName)

    pcapFileName = APKName + str(time.time()) + ".pcap"

    stackFileName = "tmpName"

    APKFilePath = APK["APKFilePath"]

    logger.debug("pcapFileName: %s", pcapFileName)
    logger.debug("packageName: %s", packageName)

    sub = subprocess.Popen(
        ["python3", "tcs.py", "-U", "-f", packageName, "-p", fileConfig["pcapFilePathPrefix"] + pcapFileName],
        bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pid = sub.pid
    time.sleep(20)

    logger.debug("starting auto click process...")
    clickProcess = startAutoClick()

    logger.debug("waiting for 180 seconds...")
    time.sleep(180)

    try:
        logger.debug("try to kill autoClick...")
        os.kill(clickProcess.pid, 9)
    except:
        logger.debug("kill autoClick failed")
        pass

    try:
        logger.debug("try to signal to capture process")
        sub.send_signal(signal.SIGINT)
    except:
        logger.debug("signal failed")
        pass

    time.sleep(5)
    logger.debug("killing capture process")
    sub.kill()
    logger.debug("killing autoClick process")
    clickProcess.kill()

    d = u2.connect('8BSX1EQGX')
    d.app_stop(packageName)
    logger.debug("stop app ok")
    logger.debug("pcapFileName: %s, stackFileName: %s" % (pcapFileName, stackFileName))

    uninsatllCommand = "adb uninstall %s" % packageName
    os.system(uninsatllCommand)
    logger.debug("apk %s uninstalled !!!" % packageName)

    return pcapFileName, stackFileName


def startAutoClick():
    subProcess = subprocess.Popen(["python3", "test.py"], bufsize=-1, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    return subProcess


if __name__ == '__main__':

    logger.info('\n==========system starting==========')
    while 1:
        APKDict = DBUtils.getUnProcessedAPKs()
        if len(APKDict) == 0:
            logger.info('no apk needs to be tested, waiting for next time...')
            time.sleep(30)
            continue
        else:
            for APK in APKDict:
                logger.info('--------start APK test--------')
                logger.debug("main pid: %s" % os.getpid())
                logger.debug("killing all children process..")
                procs = psutil.Process().children()
                for p in procs:
                    logger.debug("child process id: %s" % p.pid)
                    logger.debug("child process name: %s" % p.name())
                    p.terminate()
                result = preProcessAPK(APK)
                if result:
                    DBUtils.writePreProcessLog(APK)
                    pcapFileName, stackFileName = startCapture(APK)

                    childClickPid = startAutoClick()

                    re, logID = DBUtils.writeCaptureLog(APK, pcapFileName, stackFileName)
                    DBUtils.updateAPKFlag(APK)

                    # extractUtils.extractHTTPMetadata(APK, logID)
                    # DBUtils.updateCaptureLogFlag(APK, logID)
                else:
                    logger.warning("APK preProcess failed %s", APK["APKName"])
                    pass
                time.sleep(3)
