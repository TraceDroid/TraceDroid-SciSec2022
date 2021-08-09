import re
import urllib.request
import os
import requests
from bs4 import BeautifulSoup

load_path = "/data/liqu/"
# load_path = "../tmp/"
os.chdir(load_path)
       
class liqu:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'https://os-android.liqucn.com/rj/'

    def geturl(self):
        self.urllist.append(self.baseurl)
        for i in range(10000, 15000):
            self.urllist.append(self.baseurl + '?page={}'.format(i))
            # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            header = {}
            header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(i)
            try:
                req = urllib.request.Request(self.urllist[i], headers=header)
                response = urllib.request.urlopen(req)
            except Exception as e:
                # print("url error")
                continue
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('div', class_ = 'tip_list')
            # print(html[0])
            for j in range(len(html)):
                tmp = str(html[j]).split('href="')[1]
                detail_url = tmp.split('" ')[0]
                file_name = detail_url.split('/')[-1]
                header = {}
                header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(file_name)
                file_name = file_name.split('.')[0] + '.apk'

                req = urllib.request.Request(detail_url, headers=header)
                detail = urllib.request.urlopen(req)
                download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='btn_android')
                download_url = str(download_url).split('href="')[1]
                download_url = download_url.split('" ')[0]
                # print(download_url)
                file_path = load_path + file_name
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    response = requests.get(download_url, headers=header, stream=True)
                    with open(file_name, "wb") as code:
                        code.write(response.content)
                    # urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    print(e)
                    continue

    def start(self):
        self.geturl()
        self.spider()
       
if __name__ == '__main__':

    yyb = liqu()
    yyb.start()