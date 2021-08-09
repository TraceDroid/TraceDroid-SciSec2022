import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/zol/"
# load_path = './tmp/'
os.chdir(load_path)
       
class zol:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'https://sj.zol.com.cn/mobilesoft/page_{}.html'

    def geturl(self):
        for i in range(1, 87):
            self.urllist.append(self.baseurl.format(i))
        # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('li', class_ = 'game-item clearfix')
            for j in range(len(html)):
                try:
                # print(html[j])
                    tmp = str(html[j]).split('href=" ')[1]
                    detail_url = tmp.split('" ')[0]
                    detail = urllib.request.urlopen(detail_url)
                    download_url = BeautifulSoup(detail, 'html.parser').find('a', id='down_main_android')
                    download_url = str(download_url).split("corpsoft('")[1]
                    download_url = download_url.split("'")[0]
                    file_name = download_url.split('softid=')[1]
                    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(file_name),
                              "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                              "Accept-Language" : "zh-CN,zh;q=0.9",
                              "Accept-Encoding" : "gzip, deflate, br",
                              "DNT" : "1",
                              "Connection" : "close",
                              'Referer': 'https://sj.zol.com.cn/mobilesoft/'
                    }
                    file_name = file_name.split('&')[0] + '.apk'
                    # print(download_url)
                    # print(file_name)
                    file_path = load_path + file_name
                    try:
                        if os.path.exists(file_path):
                            print("apk exists")
                            continue

                        response = requests.get(download_url, headers=header, stream=True)
                        with open(file_name, "wb") as code:
                            code.write(response.content)
                        # urllib.request.urlretrieve(download_url, './tmp/' + file_name)
                        print("downloading success")
                    except Exception as e:
                        print("download failed")
                        print(e)
                        continue
                except Exception as e:
                    print('url error')
                    continue

    def start(self):
        self.geturl()
        self.spider()
       
if __name__ == '__main__':

    yyb = zol()
    yyb.start()