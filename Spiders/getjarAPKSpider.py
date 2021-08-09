import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/getjar/"
# load_path = './tmp/'
os.chdir(load_path)

header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
       
class getjar:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'https://www.getjar.com/mobile-apps/{}/'

    def geturl(self):
        for i in range(1, 4730):
            self.urllist.append(self.baseurl.format(i))


    def spider(self):
        for i in range(len(self.urllist)):
            req = urllib.request.Request(url=self.urllist[i], headers=header)
            response = urllib.request.urlopen(req)
            html = response.readlines()
            link_list = []
            for j in range(len(html)):
                tmp = str(html[j])
                if '" href="/categories/' in tmp:
                    detail_url = tmp.split('href="')[1]
                    detail_url = 'https://www.getjar.com' + detail_url.split('">')[0]
                    link_list.append(detail_url)
            # print(link_list)
            for detail_url in link_list:
                detail = requests.get(detail_url, headers=header)
                html = BeautifulSoup(detail.content, 'html.parser')
                try:
                    categoryid = html.find('div', class_='media')
                    categoryid = str(categoryid).split('getjar.com/')[2]
                    categoryid = categoryid.split('"')[0]
                    categoryid = categoryid.split('/')[1]
                    # print(categoryid)
                    file_name = html.find('b', class_='apkfn')
                    file_name = str(file_name).split('>')[1]
                    file_name = file_name.split('<')[0]
                    # print(file_name)
                    appid = html.find('a', class_ = 'report')
                    appid = str(appid).split('appID=')[1]
                    appid = appid.split('"')[0]
                    # print(appid)
                    download_file_name = file_name.replace(' ', '%20')
                    download_url = 'http://download.getjar.com/download/{}/{}?a={}'.format(categoryid, download_file_name, appid)

                    file_name = file_name.split('_')[-1]
                    file_path = load_path + file_name
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                    continue
                except Exception as e:
                    print("something error, download failed")
                    continue


    def start(self):
        self.geturl()
        self.spider()
       
if __name__ == '__main__':

    yyb = getjar()
    yyb.start()