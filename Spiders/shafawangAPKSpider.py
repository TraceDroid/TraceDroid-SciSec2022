import re
import urllib.request
import os
from bs4 import BeautifulSoup
import string

load_path = "/data/shafawang/"
os.chdir(load_path)

class shafawang:
    def __init__(self):
        self.urllist = []
        self.baseurl = ''
    

    def geturl(self):
        for i in range(1, 29):
            self.baseurl = 'http://app.shafa.com/list/app/?sort_by=downloads&page=%d'.format(i)
            self.urllist.append(self.baseurl)
            # print(self.baseurl)

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'app-item-element')
            # print(html)
            link_list = []
            for j in range(len(html)):
                tmp = str(html[j]).split('href="')[1]
                detail_url = tmp.split('" ')[0]
                file_name = str(html[j]).split("')")[0]
                file_name = file_name.split(" '")[-1] + '.apk'
                file_path = load_path + file_name
                detail = urllib.request.urlopen(detail_url)
                download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='btn btn-success btn-lg pull-right')
                download_url = str(download_url).split('data-url="')[1]
                download_url = download_url.split('" ')[0]
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

    yyb = shafawang()
    yyb.start()       