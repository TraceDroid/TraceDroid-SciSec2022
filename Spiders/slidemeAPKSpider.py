import re
import urllib.request
import os
from bs4 import BeautifulSoup
import json
import requests

load_path = "/data/slideme/"
# load_path = '../tmp/'
os.chdir(load_path)

       
class APKSpider:
    def __init__(self, category):
        self.urllist = []
        self.baseurl = 'http://slideme.org/applications?page={}&filters=tid%' + category + '&solrsort=tfs_price%20asc'

    def spider(self):
        for i in range(603):
            response = urllib.request.urlopen(self.baseurl.format(i))
            # print(self.baseurl.format(i))
            html = BeautifulSoup(response, 'html.parser')
            apps = html.find_all('div', class_='node node-mobileapp')
            # print(apps)
            for app in apps:
                if '<div class="price">Free</div>' in str(app):
                    detail_url = str(app).split('"title"><a href="')[1]
                    detail_url = 'http://slideme.org' + detail_url.split('">')[0]
                    file_name = detail_url.split('/')[-1] + '.apk'
                    # print(file_name)
                    detail = urllib.request.urlopen(detail_url)
                    html = BeautifulSoup(detail, 'html.parser')
                    download_url = html.find('div', class_='download-button')
                    download_url = str(download_url).split('href="')[1]
                    download_url = download_url.split('"')[0]
                    # print(download_url)
                    file_path = load_path + file_name
                    try:
                        if os.path.exists(file_path):
                            print("apk exists")
                            continue
                        response = requests.get(download_url)
                        with open(file_name, "wb") as code:
                            code.write(response.content)
                        # urllib.request.urlretrieve(download_url, file_name)
                        print("downloading success")
                    except Exception as e:
                        print("download failed")
                        print(e)
                        continue
                else:
                    return

    def start(self):
        self.spider()
       
if __name__ == '__main__':

    categories = ['3A83570', '3A83286', '3A83590', '3A17754', '3A21', '3A25',
                  '3A24', '3A20', '3A83534', '3A71', '3A22', '3A14',
                  '3A26', '3A16', '3A9241', '3A83628', '3A18', '3A28', '3A19']
    for category in categories:
        yyb = APKSpider(category)
        yyb.start()