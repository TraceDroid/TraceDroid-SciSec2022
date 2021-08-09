import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/pconline/"
# load_path = './tmp/'
os.chdir(load_path)
       
class pconline:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'https://dl.pconline.com.cn/sort/1402-1-{}.html'

    def geturl(self):
        for i in range(1, 14231):
            self.urllist.append(self.baseurl.format(i))
        # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'btn')
            for j in range(len(html)):
                tmp = str(html[j]).split('href="')[1]
                detail_url = 'https:' + tmp.split('" ')[0]
                file_name = detail_url.split('/')[-1]
                file_name = file_name.split('.')[0] + '.apk'
                # print(detail_url)
                # print(file_name)
                detail = urllib.request.urlopen(detail_url)
                download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='btn dl-btn new-dl-btn')
                download_url = str(download_url).split('tempurl="')[1]
                download_url = 'https:' + download_url.split('">')[0]
                # print(download_url)
                # print(file_name)
                file_path = load_path + file_name
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    print(e)
                    continue

    def start(self):
        self.geturl()
        self.spider()
       
if __name__ == '__main__':

    yyb = pconline()
    yyb.start()