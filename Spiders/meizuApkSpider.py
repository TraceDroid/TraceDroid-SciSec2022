import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/meizu/"
# load_path = "./tmp/"
os.chdir(load_path)

class ppzhushou:
    def __init__(self, category):
        self.baseurl = 'http://app.meizu.com/apps/public/category/{}/all/new/index/0/18'.format(category)
        # print(self.baseurl)

    def spider(self):
        response = urllib.request.urlopen(self.baseurl)
        html = BeautifulSoup(response, 'html.parser')
        html = html.find_all('div', class_='one_right')
        for j in range(len(html)):
            tmp = str(html[j])
            # print(tmp)
            file_name = tmp.split('package_name=')[1]
            file_name = file_name.split('">')[0] + '.apk'
            appid = tmp.split('appid="')[1]
            appid = appid.split('"')[0]
            # print(appid)
            # print(file_name)
            detail_url = 'http://app.meizu.com/apps/public/download.json?app_id={}'.format(appid)
            response = requests.get(url=detail_url)
            j = json.loads(str(response.text))
            download_url = j['value']['downloadUrl']
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
        self.spider()

if __name__ == '__main__':

    category_list = [9014, 103, 100, 102, 106, 104, 101, 338, 339, 344, 105]
    for category in category_list:
        yyb = ppzhushou(category)
        yyb.start()


