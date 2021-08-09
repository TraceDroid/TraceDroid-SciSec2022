import platform
import re
import urllib.request
import os
import requests
from bs4 import BeautifulSoup
import cloudscraper

if platform.system().lower() == 'windows':
    load_path = "E:\\apkpure\\"
elif platform.system().lower() == 'linux':
    load_path = "/data/apkpure/"

# load_path = "./tmp/"
os.chdir(load_path)

scraper = cloudscraper.create_scraper()


class Apkpure:
    def __init__(self):
        self.urllist = []
        self.baseurl = "https://apkpure.com/{}?page={}&ajax=1"

    def geturl(self, category):
        for page in range(1, 100):
            url = self.baseurl.format(category, page)
            # print(url)
            html = scraper.get(url=url, stream=True).text
            if 'li' not in html:
                break
            else:
                self.urllist.append(url)
        # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            response = scraper.get(url=self.urllist[i], stream=True).content
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('div', class_='category-template-down')
            # print(html[0])
            for j in range(len(html)):
                detail_url = str(html[j]).split('href="')[1]
                detail_url = 'https://apkpure.com' + detail_url.split('"')[0]
                # print(detail_url)
                file_name = detail_url.split('/')[-2]
                if 'Download XAPK' in str(html[j]):
                    file_name += '.xapk'
                    continue
                else:
                    file_name += '.apk'
                # print(file_name)
                try:
                    res = scraper.get(url=detail_url, stream=True).content
                except Exception as e:
                    print(e)
                    continue
                detail = BeautifulSoup(res, 'html.parser')
                download_url = detail.find('a', id='download_link')


                # print(download_url)
                try:
                    if os.path.exists(file_name):
                        print("apk exists")
                        continue
                    download_url = str(download_url).split('href="')[1]
                    download_url = download_url.split('"')[0]
                    print("starting download %s" % download_url)
                    apk = scraper.get(download_url, stream=True)
                    with open(file_name, "wb") as code:
                        code.write(apk.content)
                    # urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except IndexError as ie:
                    print("IndexError")
                    print(ie)
                except Exception as e:
                    print("download failed")
                    print(e)
                finally:
                    continue

    def start(self):
        categories = ['health_and_fitness', 'house_and_home', 'libraries_and_demo', 'lifestyle',
                      'maps_and_navigation', 'medical', 'music_and_audio', 'news_and_magazines', 'parenting',
                      'personalization', 'photography', 'productivity', 'shopping', 'social', 'sports', 'tools',
                      'travel_and_local', 'video_players', 'weather']
        for category in categories:
            print("="*40 + category + "="*40)
            self.geturl(category)
            self.spider()


if __name__ == '__main__':
    yyb = Apkpure()
    yyb.start()
