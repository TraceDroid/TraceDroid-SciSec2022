import re
import urllib.request
import os
from bs4 import BeautifulSoup

load_path = "/data/apk20/"
os.chdir(load_path)

class fdroid:
    def __init__(self, category):
        self.urllist = []
        self.baseurl = 'https://www.apk20.com/cat/{}/'.format(category)

    def geturl(self, pages):
        self.urllist.append(self.baseurl)
        for i in range(1, pages):
            self.urllist.append(self.baseurl + 'page/{}'.format(i))
            # print(self.baseurl + '{}/index.html'.format(i))

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('h4')
            for j in range(len(html)):
                tmp = str(html[j]).split('href="https://www.apk20.com/apk/')[1]
                tmp = tmp.split('/"')[0]
                download_url = 'https://dl.apk20.com/download.php?app_id=' + tmp
                # print(download_url)
                file_name = tmp + '.apk'
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
                    continue

    def start(self, pages):
        self.geturl(pages)
        self.spider()

if __name__ == '__main__':
    categories_pages = {
        'lifestyle': 43,
        'health-fitness': 19,
        'photography': 30,
        'books-reference': 51,
        'entertainment': 65,
        'shopping': 22,
        'productivity': 39,
        'music-audio': 47,
        'sports': 40,
        'tools': 110,
        'social': 16,
        'news-magazines': 33,
        'medical': 10,
        'travel-local': 24,
        'libraries-demo': 3,
        'personalisation': 2,
        'business': 16,
        'comics': 3,
        'weather': 12,
        'finance': 7,
        'personalization': 69,
        'events': 2,
        'food-drink': 5,
        'house-home': 3,
        'beauty': 2,
        'video-players-editors': 21,
        'auto-vehicles': 3,
        'art-design': 2,
        'dating': 3,
        'maps-navigation': 16,
        'parenting': 2,
    }

    for category, pages in categories_pages.items():
        yyb = fdroid(category)
        yyb.start(pages)