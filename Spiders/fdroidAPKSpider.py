import re
import urllib.request
import os
from bs4 import BeautifulSoup

load_path = "/data/fdroid/"
os.chdir(load_path)
       
class fdroid:
    def __init__(self, category):
        self.urllist = []
        self.baseurl = 'https://f-droid.org/zh_Hans/categories/{}/'.format(category)

    def geturl(self, pages):
        self.urllist.append(self.baseurl)
        for i in range(2, pages):
            self.urllist.append(self.baseurl + '{}/index.html'.format(i))
            # print(self.baseurl + '{}/index.html'.format(i))

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'package-header')
            for j in range(len(html)):
                tmp = str(html[j]).split('href="')[1]
                tmp = tmp.split('">')[0]
                detail_url = 'https://f-droid.org/' + tmp
                # print(detail_url)
                file_name = tmp.split('/')[-1] + '.apk'
                # print(file_name)
                detail = urllib.request.urlopen(detail_url)
                download_url = BeautifulSoup(detail, 'html.parser').find('p', class_='package-version-download')
                download_url = str(download_url).split('href="')[1]
                download_url = download_url.split('">')[0]
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

    def start(self, pages):
        self.geturl(pages)
        self.spider()
       
if __name__ == '__main__':
    categories_pages = {
        'connectivity': 9,
        'development': 7,
        'games': 14,
        'graphics': 4,
        'internet': 20,
        'money': 5, 
        'multimedia': 16,
        'navigation': 8, 
        'phone-sms': 5,
        'reading': 8, 
        'science-education': 10, 
        'security': 7,
        'sports-health': 6,
        'system': 20,
        'theming': 7,
        'time': 8,
        'writing': 8,
    }

    for category, pages in categories_pages.items():
        yyb = fdroid(category)
        yyb.start(pages)