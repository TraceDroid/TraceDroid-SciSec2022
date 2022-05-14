import urllib.request
import os
import re
import json

class AppSipder:
    def __init__(self):
        #URL模式：http://shouji.baidu.com/software/502/list_x.html,分成三个部分
        self.base_URL = 'http://shouji.baidu.com/software/'
        #类别数字
        self.category_num = [501, 502, 503, 504, 505, 506, 507, 508, 509, 510]
        # self.category_num = [501]
        #分页编号
        self.page_num = [1, 2, 3, 4, 5, 6, 7, 8]
        # self.page_num = [1]



    #获得所有应用 类别 页的url
    def getAppCategoryPageURL(self):
        #所有应用类别的URLlist
        categoryPageURL_list = []
        for x in self.category_num:
            for y in self.page_num:
                categoryPageURL_list.append(self.base_URL + str(x) + '/list_' + str(y) + '.html')
        return categoryPageURL_list

    #爬取所有应用 详情 页的url
    def getAppDetailPageURL(self):
        categoryPageURL_list = self.getAppCategoryPageURL()
        appDetailPageURL_list = []
        for url in categoryPageURL_list:
            #构造request请求对象
            response = urllib.request.urlopen(url)
            html = response.readlines()
            for i in range(len(html)):
                if 'app-box' in str(html[i]):
                    # print(html[i])
                    tmp = str(html[i]).split('href="')[1]
                    tmp = tmp.split('" ')[0]
                    appDetailPageURL = 'http://shouji.baidu.com/' + tmp
                    appDetailPageURL_list.append(appDetailPageURL)
        return appDetailPageURL_list
                    # tmp = tmp.split('"')[0]
                    # link_list.append(tmp)
        #     print(url)
        #     content = str(response.read())
        #     #re模块用于对正则表达式的支持,pattern可以理解为一个匹配模式,re.S指"."可以匹配换行"\n"
        #     pattern = re.compile('<div.*?app-box">.*?<a href="(.*?)".*?>', re.S)
        #     resultStr = re.findall(pattern, content)
        #     print(resultStr)
        #     for result in resultStr:
        #         print('crawling ' + result)
        #         appDetailPageURL = 'http://shouji.baidu.com/' + result
        #         appDetailPageURL_list.append(appDetailPageURL)
        # return appDetailPageURL_list

    #爬取App详情页中的所需内容
    def getAppInfo(self, appURL):
        try:
            response = urllib.request.urlopen(appURL)
        except Exception as e:
            print(e)
        html = response.readlines()
        for i in range(len(html)):
            if 'data_url' in str(html[i]):
                data_url = str(html[i]).split('data_url="')[1][:-4]
                # print(data_url)
            if 'data_package' in str(html[i]):
                data_package = str(html[i]).split('data_package="')[1][:-4]
                # print(data_package)
                break
        file_name = data_package + ".apk"
        load_path = "/data/baidu/"
        file_path = load_path + file_name
        os.chdir(load_path)
        try:
            if os.path.exists(file_path):
                print("apk exists")
            else:
                urllib.request.urlretrieve(data_url, file_name)
                print("downloading success")
        except Exception as e:
            print("download failed")



    #爬虫开始入口
    def startSpider(self):
        # print('Start crawling please wait...')
        appDetailPageURL_list = self.getAppDetailPageURL()
        resultInfo = []
        for url in appDetailPageURL_list:
            resultInfo.append(self.getAppInfo(url))


Spider = AppSipder()
Spider.startSpider()
