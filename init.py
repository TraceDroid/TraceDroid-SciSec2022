#!/usr/bin/env python
# coding:utf-8
import configparser
import logging
import os
import re
import time
import uiautomator2 as u2

logging.config.fileConfig('log.conf')
logger = logging.getLogger('APKTestEngine')

config = configparser.ConfigParser()
config.read('./config.conf')
deviceConfig = config['device']

'''
#检查apk版本号等信息
def getAppBaseInfo(apk_path):
    get_info_command = "aapt dump badging %s" %  apk_path
    output = os.popen(get_info_command).read()
    match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(output)
    if not match:
        print(output)
        raise Exception("can't get packageinfo")

    packagename = match.group(1)
    versionCode = match.group(2)
    versionName = match.group(3)
    print(" 包名：%s \n 版本号：%s \n 版本名称：%s " % (packagename, versionCode, versionName))
    return packagename
'''


def verifyPermissions(APK):
    # d = u2.connect('8BSX1EQGX')
    # path  = os.path.abspath(apk_path)
    logger.info("deviceID %s", deviceConfig['deviceID'])
    d = u2.connect(deviceConfig['deviceID'])

    apk_path = APK["APKFilePath"]
    apkName = APK["APKName"]
    install_command = "adb install -r " + "\"" + apk_path + "\""
    # os.system(cmd)
    # package_name = getAppBaseInfo(apk_path)

    package_name = APK["packageName"]
    logger.debug("installing APK %s...", apkName)
    output = os.popen(install_command).read()

    if "Success" in output:
        try:
            logger.debug("installing APK %s successful", apkName)
            logger.debug("starting APK %s... ", apkName)
            d.app_start('%s' % package_name)
            time.sleep(5)
        except Exception as e:
            logger.debug("can't get app_info, ERROR: %s" % e)
            print(e)
            return


        for i in range(5):
            logger.debug("init round %s", i)
            try:
                '''
                if d.xpath("%更新%").wait(1):
                    d.xpath("%取消%").click()
                    logger.debug("%取消% clicked")
                if d.xpath("%更新%").wait(1):
                    d.xpath("%下次%").click()
                    logger.debug("%下次% clicked")
                if d.xpath("%更新%").wait(1):
                    d.xpath("%不%").click()
                    logger.debug("%不% clicked")
                '''
                if d.xpath("%pdate%").wait(1):
                    d.xpath("%ancel%").click()
                    logger.debug("%ancel% clicked")
                if d.xpath("%pdate%").wait(1):
                    d.xpath("%lose%").click()
                    logger.debug("%lose% clicked")
                if d.xpath("%PDATE%").wait(1):
                    d.xpath("%ANCEL%").click()
                    logger.debug("%ANCEL% clicked")
                if d.xpath("%pdate%").wait(1):
                    d.xpath("%ANCEL%").click()
                    logger.debug("%ANCEL% clicked")
                if d.xpath("%PDATE%").wait(1):
                    d.xpath("%ancel%").click()
                    logger.debug("%ancel% clicked")
            except Exception as e:
                logger.debug('click error %s' % e)
            try:
                '''
                if d.xpath("继续").wait(1):
                    d.xpath("继续").click()
                    logger.debug("继续 clicked")
                if d.xpath("开启%").wait(1):
                    d.xpath("开启%").click()
                    logger.debug("开启% clicked")
                if d.xpath("%体验%").wait(1):
                    d.xpath("%体验%").click()
                    logger.debug("%体验% clicked")
                '''
                if d.xpath("continue%").wait(1):
                    d.xpath("continue%").click()
                    logger.debug("continue% clicked")
                if d.xpath("Continue%").wait(1):
                    d.xpath("Continue%").click()
                    logger.debug("Continue% clicked")
                if d.xpath("CONTINUE%").wait(1):
                    d.xpath("CONTINUE%").click()
                    logger.debug("CONTINUE% clicked")
                if d(className='android.widget.CheckBox', clickable=True).exists():
                    d(className='android.widget.CheckBox').click()
                    logger.debug("CheckBox clicked")
                '''
                if d.xpath("%授权%").wait(1):
                    d.xpath("%授权%").click()
                    logger.debug("%授权% clicked")
                if d.xpath("%下一步%").wait(1):
                    d.xpath("%下一步%").click()
                    logger.debug("%下一步% clicked")
                if d.xpath("立即%").wait(1):
                    d.xpath("立即%").click()
                    logger.debug("立即% clicked")
                '''
                if d.xpath("同意").wait(1):
                    d.xpath("同意").click()
                    logger.debug("同意 clicked")
                if d.xpath("我同意%").wait(1):
                    d.xpath("我同意%").click()
                    logger.debug("我同意% clicked")
                if d.xpath("同意%").wait(1):
                    d.xpath("同意%").click()
                    logger.debug("同意% clicked")
                if d.xpath("ok").wait(1):
                    d.xpath("ok").click()
                    logger.debug("ok clicked")
                if d.xpath("Ok").wait(1):
                    d.xpath("Ok").click()
                    logger.debug("Ok clicked")
                if d.xpath("OK").wait(1):
                    d.xpath("OK").click()
                    logger.debug("OK clicked")
                if d.xpath("start%").wait(1):
                    d.xpath("start%").click()
                    logger.debug("start% clicked")
                if d.xpath("Start%").wait(1):
                    d.xpath("Start%").click()
                    logger.debug("Start% clicked")
                if d.xpath("START%").wait(1):
                    d.xpath("START%").click()
                    logger.debug("START% clicked")
                if d.xpath("next%").wait(1):
                    d.xpath("next%").click()
                    logger.debug("next% clicked")
                if d.xpath("Next%").wait(1):
                    d.xpath("Next%").click()
                    logger.debug("Next% clicked")
                if d.xpath("NEXT%").wait(1):
                    d.xpath("NEXT%").click()
                    logger.debug("NEXT% clicked")
                if d.xpath("%accept%").wait(1):
                    d.xpath("%accept%").click()
                    logger.debug("%accept% clicked")
                if d.xpath("%Accept%").wait(1):
                    d.xpath("%Accept%").click()
                    logger.debug("%Accept% clicked")
                if d.xpath("%ACCEPT%").wait(1):
                    d.xpath("%ACCEPT%").click()
                    logger.debug("%ACCEPT% clicked")
                if d.xpath("%agree%").wait(1):
                    d.xpath("%agree%").click()
                    logger.debug("%agree% clicked")
                if d.xpath("%Agree%").wait(1):
                    d.xpath("%Agree%").click()
                    logger.debug("%Agree% clicked")
                if d.xpath("%AGREE%").wait(1):
                    d.xpath("%AGREE%").click()
                    logger.debug("%AGREE% clicked")
                #if d.xpath("同意并继续").wait(1):
                #    d.xpath("同意并继续").click()
                #    logger.debug("同意并继续 clicked")
                '''
                if d.xpath("%知道%").wait(1):
                    d.xpath("%知道%").click()
                    logger.debug("%知道% clicked")
                if d.xpath("确定").wait(1):
                    d.xpath("确定").click()
                    logger.debug("确定 clicked")
                if d.xpath("确认").wait(1):
                    d.xpath("确认").click()
                    logger.debug("确认 clicked")
                '''
                if d.xpath("允许").wait(1):
                    d.xpath("允许").click()
                    logger.debug("允许 clicked")
            except Exception as e:
                logger.error("init error %s:" % e)

            time.sleep(1)

        try:
            #for i in range(5):
            #    d.swipe_ext("left", 0.8)
            #logger.debug('swipe finished')
            for x in  range(2):
                '''
                if d.xpath("%进入%").wait(1):
                    d.xpath("%进入%").click()
                    logger.debug("%进入% clicked")
                if d.xpath("%开启%").wait(1):
                    d.xpath("%开启%").click()
                    logger.debug("开启% clicked")
                if d.xpath("%体验%").wait(1):
                    d.xpath("%体验%").click()
                    logger.debug("%体验% clicked")
                if d.xpath("同意%").wait(1):
                    d.xpath("同意%").click()
                    logger.debug("同意% clicked")
                if d.xpath("确认%").wait(1):
                    d.xpath("确认%").click()
                    logger.debug("确认% clicked")
                if d.xpath("继续%").wait(1):
                    d.xpath("继续%").click()
                    logger.debug("继续% clicked")
                if d.xpath("%知道%").wait(1):
                    d.xpath("%知道%").click()
                    logger.debug("%知道% clicked")
                '''
                if d.xpath("continue%").wait(1):
                    d.xpath("continue%").click()
                    logger.debug("continue% clicked")
                if d.xpath("Continue%").wait(1):
                    d.xpath("Continue%").click()
                    logger.debug("Continue% clicked")
                if d.xpath("CONTINUE%").wait(1):
                    d.xpath("CONTINUE%").click()
                    logger.debug("CONTINUE% clicked")
                if d.xpath("start%").wait(1):
                    d.xpath("start%").click()
                    logger.debug("start% clicked")
                if d.xpath("Start%").wait(1):
                    d.xpath("Start%").click()
                    logger.debug("Start% clicked")
                if d.xpath("START%").wait(1):
                    d.xpath("START%").click()
                    logger.debug("START% clicked")
                if d.xpath("next%").wait(1):
                    d.xpath("next%").click()
                    logger.debug("next% clicked")
                if d.xpath("Next%").wait(1):
                    d.xpath("Next%").click()
                    logger.debug("Next% clicked")
                if d.xpath("NEXT%").wait(1):
                    d.xpath("NEXT%").click()
                    logger.debug("NEXT% clicked")
                if d.xpath("enter%").wait(1):
                    d.xpath("enter%").click()
                    logger.debug("enter% clicked")
                if d.xpath("Enter%").wait(1):
                    d.xpath("Enter%").click()
                    logger.debug("Enter% clicked")
                if d.xpath("ENTER%").wait(1):
                    d.xpath("ENTER%").click()
                    logger.debug("ENTER% clicked")
                if d.xpath("允许").wait(1):
                    d.xpath("允许").click()
                    logger.debug("允许 clicked")
        except Exception as e:
            logger.debug('something error %s' % e)

        d.app_stop('%s' % package_name)
        logger.debug('APK %s init OK!', package_name)
        return 1
    else:
        logger.warning('APK %s init failed!', package_name)
        return 0
