import platform
from typing import Any, Union

import uiautomator2 as u2
import GetXmlInformation as GXI
import os
import hashlib
import time
import logging.config
import logging.handlers

logging.config.fileConfig('TestEngine.conf')
logger = logging.getLogger('TestEngine')

# 全局变量xml的存储路径
if platform.system().lower() == 'windows':
    filePath = "C:\\AppXml"
elif platform.system().lower() == 'linux':
    filePath = "/home/chj/XMLTree"

# 全局变量
# coordCurPosInArray = {0:0, 1:0, 2:0, 3:0, 4:0}  # 当前页面的坐标遍历到了那个位置
xmlHashDict = {}  # 存放xml的tree:level的值


def processAppToGetUIXml(device_id):
    index = 0
    d = u2.connect(device_id)

    # d.click_post_delay = 0.7  #    每次点击的等待的时间
    d.settings["operation_delay"] = (0, 0.8)
    d.settings['operation_delay_methods'] = ["click"]
    # d.click(0, 0)  # 点击屏幕上的某一个固定位置，然后打开该应用  或者是通过adb获取当前安装好的应用，然后通过获取包名来执行应用
    appPackage = d.current_app()['package']  # 打印当前界面对应的app的包名和启动的activity（最好是开始就进入mainActivity）
    fileDir = filePath + "/" + appPackage
    helpXmlName = fileDir + "/" + 'help.xml'  # 辅助文件，用来每次存取当前遍历界面的布局树
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    fileName = fileDir + "/" + d.current_app()['activity'] + '_' + str(
        index) + '_' + '0' + '.xml'  # 第0层当前activity的布局文件名
    index = index + 1
    xml = d.dump_hierarchy()  # 获取当前界面的xml信息
    writeToTxt(xml, fileName)  # 将布局文件写入文本，待读取分析
    node_list = GXI.getXmlData(fileName)  # 从布局文件中分析出node_list, 格式为[level,class,clickable,checkable,bounds]，其中bounds的格式为“[x1.y1][x2,y2]”
    """
    getStrHash:计算字符串的MD5值
    getXmlTreeMapToStr：将XML树结构转换为字符串
    xmlHashDict：字典，用于存储xml的hash值
    将当前activity的布局结构转换为String，并对该String计算MD5值，以此来判断当前页面是否已经遍历过
    xmlHashDict是字典其中存储的是当前activity的布局字符串的MD5
    """
    xmlHashDict[getStrHash(GXI.getXmlTreeMapToStr(node_list))] = 0  # key是当前activity布局树字符串的MD5值，value为0，即代表第0层
    """
    click_coord_list: 当前activity可点击的坐标列表，每个列表是[x,y]的形式
    """
    click_coord_list = getClickCoord(node_list)
    logger.debug("clickCoord0: " + str(click_coord_list))
    curActivity_0 = d.current_app()['activity']
    for i in range(0, click_coord_list.__len__()):  # 初始层
        if d.current_app()['package'] == appPackage:
            # while(d.current_app()['activity'] != curActivity_0 and d.current_app()['package'] == appPackage):
            #     d.press('back')
            d.click(click_coord_list[i][0], click_coord_list[i][1])  # 点一下
            #time.sleep(0.8)
            if d.current_app()['activity'].lower().__contains__('WebViewActivity'.lower()):
                time.sleep(2)  # 等待界面加载完成
            xml = d.dump_hierarchy()  # 再次dump当前activity，用于判断是否是新界面
            writeToTxt(xml, helpXmlName)
            xmlHash = getStrHash(GXI.getXmlTreeMapToStr(GXI.getXmlData(helpXmlName)))  # 当前界面对应的布局树的MD5值
            if xmlHashDict.__contains__(xmlHash):  #  如果xmlHashDict中已经包含了当前的MD5值，就说明这个activity已经遍历过了，
                num = xmlHashDict[xmlHash]
                for i_0 in range(0, num):  # 如果说遍历过了，并且界面是比当前界面更深的层次则返回当前层
                    d.press('back')
            else:
                if d.current_app()['package'] == appPackage:
                    xmlHashDict[xmlHash] = 1
                    fileName = fileDir + "/" + d.current_app()['activity'] + '_' + str(index) + '_' + '1' + '.xml'
                    index = index + 1
                    writeToTxt(xml, fileName)
                    if not d.current_app()['activity'].lower().__contains__('WebViewActivity'.lower()):
                        clickCoord1 = getClickCoord(GXI.getXmlData(fileName))  # 获取当前界面上可点击的元素
                        curActivity_1 = d.current_app()['activity']
                        if clickCoord1.__len__() == 0:
                            d.press('back')
                        else:
                            for j in range(0, clickCoord1.__len__()):  # 第二层
                                if d.current_app()['package'] == appPackage:
                                    d.click(clickCoord1[j][0], clickCoord1[j][1])
                                    #time.sleep(0.8)
                                    if d.current_app()['activity'].lower().__contains__('WebViewActivity'.lower()):
                                        time.sleep(2)  # 等待界面加载完成
                                    xml = d.dump_hierarchy()
                                    writeToTxt(xml, helpXmlName)
                                    xmlHash = getStrHash(
                                        GXI.getXmlTreeMapToStr(GXI.getXmlData(helpXmlName)))  # 当前界面对应的布局树的映射
                                    if xmlHashDict.__contains__(xmlHash):
                                        num = xmlHashDict[xmlHash]
                                        if num < 1:  # 如果说点击了返回到了上一层
                                            d.click(click_coord_list[i][0], click_coord_list[i][1])
                                            #time.sleep(0.8)
                                        elif num == 1:
                                            if curActivity_1 != d.current_app()['activity']:
                                                d.press('back')
                                        else:
                                            d.press('back')
                                    else:
                                        if d.current_app()['package'] == appPackage:
                                            xmlHashDict[xmlHash] = 2
                                            fileName = fileDir + "/" + d.current_app()['activity'] + '_' + str(
                                                index) + '_' + '2' + '.xml'
                                            index = index + 1
                                            writeToTxt(xml, fileName)
                                            if not d.current_app()['activity'].lower().__contains__(
                                                    'WebViewActivity'.lower()):  # 第三层
                                                clickCoord2 = getClickCoord(GXI.getXmlData(fileName))  # 获取当前界面上可点击的元素
                                                curActivity_2 = d.current_app()['activity']
                                                if clickCoord2.__len__() == 0:
                                                    d.press('back')
                                                else:
                                                    for k in range(0, clickCoord2.__len__()):  # 第三层
                                                        if d.current_app()['package'] == appPackage:
                                                            d.click(clickCoord2[k][0], clickCoord2[k][1])
                                                            #time.sleep(0.8)
                                                            if d.current_app()['activity'].lower().__contains__(
                                                                    'WebViewActivity'.lower()):
                                                                time.sleep(1.5)  # 等待界面加载完成
                                                            xml = d.dump_hierarchy()
                                                            writeToTxt(xml, helpXmlName)
                                                            xmlHash = getStrHash(GXI.getXmlTreeMapToStr(
                                                                GXI.getXmlData(helpXmlName)))  # 当前界面对应的布局树的映射
                                                            if xmlHashDict.__contains__(xmlHash):
                                                                num = xmlHashDict[xmlHash]
                                                                if num < 2:  # 如果说点击了返回到了上一层
                                                                    d.click(clickCoord1[j][0], clickCoord1[j][1])
                                                                    #time.sleep(0.8)
                                                                elif num == 2:
                                                                    if curActivity_2 != d.current_app()['activity']:
                                                                        d.press('back')
                                                                else:
                                                                    d.press('back')
                                                            else:
                                                                if d.current_app()['package'] == appPackage:
                                                                    xmlHashDict[xmlHash] = 3
                                                                    fileName = fileDir + "/" + d.current_app()[
                                                                        'activity'] + '_' + str(
                                                                        index) + '_' + '3' + '.xml'
                                                                    index = index + 1
                                                                    writeToTxt(xml, fileName)
                                                                    if not d.current_app()[
                                                                        'activity'].lower().__contains__(
                                                                            'WebViewActivity'.lower()):  # 第四层
                                                                        clickCoord3 = getClickCoord(
                                                                            GXI.getXmlData(fileName))  # 获取当前界面上可点击的元素
                                                                        curActivity_3 = d.current_app()['activity'];
                                                                        if clickCoord3.__len__() == 0:
                                                                            d.press('back')
                                                                        else:
                                                                            for m in range(0,
                                                                                           clickCoord3.__len__()):  # 第四层
                                                                                if d.current_app()[
                                                                                    'package'] == appPackage:
                                                                                    d.click(clickCoord3[m][0],
                                                                                            clickCoord3[m][1])
                                                                                    #time.sleep(0.8)
                                                                                    if d.current_app()[
                                                                                        'activity'].lower().__contains__(
                                                                                            'WebViewActivity'.lower()):
                                                                                        time.sleep(1.5)  # 等待界面加载完成
                                                                                    xml = d.dump_hierarchy()
                                                                                    writeToTxt(xml, helpXmlName)
                                                                                    xmlHash = getStrHash(
                                                                                        GXI.getXmlTreeMapToStr(
                                                                                            GXI.getXmlData(
                                                                                                helpXmlName)))  # 当前界面对应的布局树的映射
                                                                                    if xmlHashDict.__contains__(
                                                                                            xmlHash):
                                                                                        num = xmlHashDict[xmlHash]
                                                                                        if num < 3:  # 如果说点击了返回到了上一层
                                                                                            d.click(clickCoord2[k][0],
                                                                                                    clickCoord2[k][1])
                                                                                        elif num == 3:
                                                                                            if curActivity_3 != \
                                                                                                    d.current_app()[
                                                                                                        'activity']:
                                                                                                d.press('back')
                                                                                        else:
                                                                                            d.press('back')
                                                                                    else:
                                                                                        if d.current_app()[
                                                                                            'package'] == appPackage:
                                                                                            xmlHashDict[xmlHash] = 4
                                                                                            fileName = fileDir + "/" + \
                                                                                                       d.current_app()[
                                                                                                           'activity'] + '_' + str(
                                                                                                index) + '_' + '4' + '.xml'
                                                                                            index = index + 1
                                                                                            writeToTxt(xml, fileName)
                                                                                            if d.current_app()[
                                                                                                'activity'].lower().__contains__(
                                                                                                    'WebViewActivity'.lower()):
                                                                                                if d(text="关闭").exists:
                                                                                                    d(text="关闭").click()
                                                                                                elif d(
                                                                                                        text="退出").exists:
                                                                                                    d(text="退出").click()
                                                                                                else:
                                                                                                    d.press('back')
                                                                                            else:
                                                                                                d.press('back')
                                                                                        else:
                                                                                            pressWhenExitAppToSystem(d,
                                                                                                                     appPackage)
                                                                                else:
                                                                                    pressWhenExitAppToSystem(d,
                                                                                                             appPackage)
                                                                    else:
                                                                        if d(text="关闭").exists:
                                                                            d(text="关闭").click()
                                                                        elif d(text="退出").exists:
                                                                            d(text="退出").click()
                                                                        else:
                                                                            pressWhenExitAppToSystem(d, appPackage)
                                                                else:
                                                                    pressWhenExitAppToSystem(d, appPackage)
                                                        else:
                                                            pressWhenExitAppToSystem(d, appPackage)
                                                    d.press('back')  # 第三层遍历完成，然后点击返回
                                            else:
                                                if d(text="关闭").exists:
                                                    d(text="关闭").click()
                                                elif d(text="退出").exists:
                                                    d(text="退出").click()
                                                else:
                                                    pressWhenExitAppToSystem(d, appPackage)
                                        else:
                                            pressWhenExitAppToSystem(d, appPackage)
                                else:
                                    pressWhenExitAppToSystem(d, appPackage)
                            d.press('back')  # 第二层遍历完成，然后点击返回
                    else:
                        if d(text="关闭").exists:
                            d(text="关闭").click()
                        elif d(text="退出").exists:
                            d(text="退出").click()
                        else:
                            pressWhenExitAppToSystem(d, appPackage)
                else:
                    pressWhenExitAppToSystem(d, appPackage)
        else:
            pressWhenExitAppToSystem(d, appPackage)


# 获取设备的信息
def getDeviceInformation(device_id):
    d = u2.connect(device_id)
    print(d.info)  # 应用信息
    print(d.device_info)  # 设备信息
    appInfo = d.current_app()  # 打印当前界面对应的app的包名和启动的activity（最好是开始就进入mainActivity)
    print(appInfo)


# 写入文件
def writeToTxt(xml, fileName):
    # startStr = '<node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.android.systemui"'
    # endStr = '<node index="3" text="" resource-id="com.android.systemui:id/scrim_in_front" class="android.view.View" package="com.android.systemui" content-desc="" ' \
    #          'checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" ' \
    #          'long-clickable="false" password="false" selected="false" visible-to-user="true" bounds="[0,0][1080,72]" />\r\n  </node>\r\n'
    #
    # xml = xml.replace(xml[xml.find(startStr):(xml.find(endStr) + len(endStr))], '')  # 把手机最上方的电量显示栏去掉
    # xml = xml.replace('\r\n', '\r')
    # state = 'rotation="0" state=' + '"' + str(2) + '"'  # state表示所在层次的
    # xml = xml.replace('rotation="0"', state)
    f = open(fileName, 'w', encoding='utf-8')
    f.write(xml)  # 这里的\n的意思是在源文件末尾换行，即新加内容另起一行插入。
    f.close()  # 特别注意文件操作完毕后要close


# 获取点击的坐标
def getClickCoord(node_list):
    clickCoord = GXI.getClickableCoordinate(node_list)
    return clickCoord


# 获取xml的信息
def getXmlInfo(fileName):
    result = GXI.getXmlData(fileName)
    return result


# 计算字符串的hash值
def getStrHash(str):
    md5 = hashlib.md5()
    md5.update(bytes(str, encoding='utf-8'))
    return md5.hexdigest()


# 当点击应用不小心退出到系统界面或其他应用时
def pressWhenExitAppToSystem(d, appPackage):  # d == device
    # if d.current_app()['package'] == 'com.huawei.android.launcher':
    if d.current_app()['package'].__contains__('com.google.'):
        d.app_start(appPackage)  # 在初始层界面就点击退出了当前应用时，要返回当前应用，并且退出之后的那个点的坐标下一个开始遍历
        # 为了应用打开时的过滤广告
        if d(text="跳过").exists:
            d(text="跳过").click()
        elif d(text="跳过广告").exists:
            d(text="跳过广告").click()
        elif d(text="关闭").exists:
            d(text="关闭").click()
        elif d(text="关闭广告").exists:
            d(text="关闭广告").click()
    else:
        d.press('back')


# 重启应用
def restartApp(d, appPackage):
    d.app_stop(appPackage)
    time.sleep(2)
    pressWhenExitAppToSystem(d, appPackage)
