import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/sougou/"
os.chdir(load_path)
       
class liqu:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'http://zhushou.sogou.com/apps/list/0-0.html?act=getapp&page='

    def geturl(self):
        for i in range(1, 11):
            self.urllist.append(self.baseurl + str(i))
        # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            response = requests.get(url=self.urllist[i])
            j = json.loads(str(response.text))
            for x in j['data']:
                file_name = x['packagename'] + '.apk'
                app_id = x['app_id']
                download_url = 'http://data.zhushou.sogou.com/app/download.html?appid={}&source=cooperation&_s=web'.format(app_id)

                file_path = load_path + file_name
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    continue

    def start(self):
        self.geturl()
        self.spider()
       
if __name__ == '__main__':

    yyb = liqu()
    yyb.start()