# -*- coding: utf-8 -*-
# @Time : 2021/4/16 18:11
# @Author : *
# @Site :
# @File : xiaomiAPPStoreSpider.py
# @Software: PyCharm
import configparser
import logging.config
import logging.handlers
import os
import urllib

import requests
from bs4 import BeautifulSoup
import DBUtils

logging.config.fileConfig('log.conf')
logger = logging.getLogger('APKTestEngine')


logger.debug("========== start spider xiaomi apps ==========")

_root_url = "http://app.mi.com"
rootPath = "/home/chj/APKTestEngine/APKFileDir/xiaomi/"
page_num = 1

while page_num < 20:
    logger.debug("开始爬取第"+str(page_num)+"页")
    wbdata = requests.get("http://app.mi.com/catTopList/5?page="+str(page_num)).text
    soup = BeautifulSoup(wbdata, "html.parser")
    links = soup.find_all("h5")
    # print(links)
    linksize = len(links)
    for i in range(linksize):
        link = links[i].contents[0]
        # print(link)
        foldername = link.string
        # print(str(foldername))
        logger.debug("foldername is: %s" % foldername)
        if foldername == '应用分发' or foldername == '开发者服务' or foldername == '联系我们':
            break
        else:
            # logger.debug(foldername)
            pass
        detail_link = urllib.parse.urljoin(_root_url, str(link["href"]))
        # print(detail_link)  #获取了下载页面的网址
        package_name = detail_link.split("=")[1]
        apkName = package_name + ".apk"
        apkPath = rootPath + apkName
        # print(package_name)
        # print(package_name)  #获取了包名,可以全部显示
        try:
            download_page = requests.get(detail_link).text
        except Exception as e:
            continue
        soup1 = BeautifulSoup(download_page, "html.parser")
        try:
            download_link = soup1.find(class_="download")["href"]
            # logger.debug("download_link is: %s" % download_link)
            # print(download_link)
        except Exception as e:
            failed = open("/home/chj/APKTestEngine/APKFileDir/xiaomi/failed(xiaomi).txt", "a+", encoding="utf-8")
            failed.write(foldername+':'+'download_link:'+download_link+'\n')
            failed.close()
            continue
        try:
            download_url = urllib.parse.urljoin(_root_url, str(download_link))   #获取了下载路径
            # print("download_url is:%s" % download_url)
            logger.debug("download_url is: %s" % download_url)
        except Exception as e:
            failed = open("/home/chj/APKTestEngine/APKFileDir/xiaomi/failed(xiaomi).txt", "a+", encoding="utf-8")
            failed.write(foldername+':'+'download_url:'+download_url+'\n')
            failed.close()
            continue
        try:
            if os.path.exists(apkPath):
                logger.debug("%s apk existed" % package_name)
                break
            else:
                logger.debug("start downloading apk %s" % package_name)
                #os.makedirs("E:\\xiaomi\\"+str(package_name)) #创建目录文件夹
                # print("file created")
                # full_path = "E:\\xiaomi\\"+str(foldername)+"\\"+str(foldername)+".txt"
                # file = open(full_path, "a+", encoding="utf-8")
        except Exception as e:
            failed = open("/home/chj/APKTestEngine/APKFileDir/xiaomi/failed(xiaomi).txt", "a+", encoding="utf-8")
            failed.write(foldername+'\n')
            failed.close()
            continue
        # localpath = os.path.join("E:\\xiaomi\\"+str(foldername), package_name+".exe")
        os.chdir(rootPath)
        # print(os.getcwd())
        try:
            # urllib.request.urlretrieve(download_url, Loadpath)
            urllib.request.urlretrieve(download_url, apkName)
            logger.debug("download apk %s success" % package_name)
            # print("download apk success")
        except Exception as e:
            # print("download failed")
            logger.debug(e)
            logger.debug("download apk FAILED")
            failed = open("/home/chj/APKTestEngine/APKFileDir/xiaomi/failed(xiaomi).txt", "a+", encoding="utf-8")
            failed.write(foldername+':'+'download_url:'+download_url+'\n')
            failed.close()
            continue

        #以下是写入数据库的代码
        logger.debug("***** start writing Metadata to DB *****")
        DBUtils.writeAPKMetaData(APPName=foldername, APKName=apkName, packageName=package_name, APKFilePath=apkPath, APKStoreName="xiaomi", needAnalyse=1)
        logger.debug("***** log finished *****")


    page_num = page_num + 1
