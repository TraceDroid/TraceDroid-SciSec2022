import re
import urllib.request
import os
from bs4 import BeautifulSoup
import string

load_path = "/data/yingyonghui/"
os.chdir(load_path)
       
class yingyonghui:
    def __init__(self):
        self.urllist = []
        self.baseurl = ''
    

    def geturl(self, pageindex):
        for i in range(1, pageindex):
            self.baseurl = 'http://www.appchina.com/category/30/1_1_{}_1_0_0_0.html'.format(i)
            self.urllist.append(self.baseurl)
            # print(self.baseurl)

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'download-now')
            # print(html)
            link_list = []
            for j in range(len(html)):
                if 'yugao-button' not in str(html[j]):
                    tmp = str(html[j]).split('href="')[1]
                    tmp = tmp.split('">')[0]
                    detail_url = 'http://www.appchina.com' + tmp
                    # print(detail_url)
                    file_name = tmp.split('/')[2] + '.apk'
                    # print(file_name)
                    file_path = load_path + file_name

                    detail = urllib.request.urlopen(detail_url)
                    try:
                        download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='download_app')
                        download_url = str(download_url).split("this,'")[1]
                        download_url = download_url.split("')")[0]
                        if os.path.exists(file_path):
                            print("apk exists")
                            continue
                        urllib.request.urlretrieve(download_url, file_name)
                        print("downloading success")
                    except Exception as e:
                        print("download failed")
                        continue
        

    def start(self):
        self.geturl(3321)
        # self.geturl(2)

        self.spider()


       
if __name__ == '__main__':

    yyb = yingyonghui()
    yyb.start()       