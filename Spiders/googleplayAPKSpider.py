import platform
import re
import urllib.request
import os
import requests
from bs4 import BeautifulSoup
import cloudscraper

if platform.system().lower() == 'windows':
    load_path = "E:\\googleplay\\"
elif platform.system().lower() == 'linux':
    load_path = "/data/googleplay/"
# load_path = "./tmp/"
os.chdir(load_path)

scraper = cloudscraper.create_scraper()


class GooglePlay:
    def __init__(self):
        self.urllist = []
        self.baseurl = "https://www.androidrank.org/android-most-popular-google-play-apps?start={}&sort=0&price=free&category={}"

    def geturl(self, category):
        for start in range(1, 42, 20):  # start=[1, 21, 41]爬前三页共60个
            url = self.baseurl.format(start, category)
            self.urllist.append(url)
            # break
        # print(self.urllist)

    def spider(self):
        for i in range(len(self.urllist)):
            response = requests.get(url=self.urllist[i], stream=True).content
            html = BeautifulSoup(response, 'html.parser')
            odd = html.find_all('tr', class_='odd')
            even = html.find_all('tr', class_='even')
            html = odd + even
            # print(html[0])
            for j in range(len(html)):
                apkname = str(html[j]).split('href="')[1]
                apkname = apkname.split('"')[0]
                apkname = apkname.split('/')[-1]
                # print(apkname)
                file_name = apkname + '.apk'
                if os.path.exists(file_name):
                    print("apk exists")
                    continue
                detail_url = 'https://play.google.com/store/apps/details?id=' + apkname
                # print(detail_url)

                try:
                    apkdl_detail_url = 'https://apk-dl.com/search?q=' + detail_url
                    response = scraper.get(url=apkdl_detail_url, stream=True).content
                    download_url = BeautifulSoup(response, 'html.parser')
                    download_url = download_url.find('div', class_='download-btn')
                    download_url = str(download_url).split('href="/')[1]
                    download_url = 'https://apk-dl.com/' + download_url.split('"')[0]
                    # print(download_url)
                    response = scraper.get(url=download_url, stream=True, allow_redirects=False).content
                    download_url = BeautifulSoup(response, 'html.parser')
                    download_url = download_url.find('a', rel='nofollow')
                    download_url = str(download_url).split('href="')[1]
                    download_url = download_url.split('"')[0]
                    # print(download_url)
                    response = scraper.get(url=download_url, stream=True).content
                    detail = BeautifulSoup(response, 'html.parser')
                    download_url = detail.find('a', class_='mdl-button')
                    # print(download_url)
                    download_url = str(download_url).split('href="')[1]
                    download_url = 'https:' + download_url.split('"')[0]
                    # print(download_url)
                    apk = scraper.get(download_url, stream=True)
                    with open(file_name, "wb") as code:
                        code.write(apk.content)
                    # urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    # print(e)
                    continue

    def start(self):
        categories = ['ART_AND_DESIGN', 'AUTO_AND_VEHICLES', 'BEAUTY', 'BOOKS_AND_REFERENCE', 'BUSINESS',
                      'COMICS', 'COMMUNICATION', 'DATING', 'EDUCATION', 'ENTERTAINMENT', 'EVENTS', 'FINANCE',
                      'FOOD_AND_DRINK', 'HEALTH_AND_FITNESS', 'HOUSE_AND_HOME', 'LIBRARIES_AND_DEMO', 'LIFESTYLE',
                      'MAPS_AND_NAVIGATION', 'MEDICAL', 'MUSIC_AND_AUDIO', 'NEWS_AND_MAGAZINES', 'PARENTING',
                      'PERSONALIZATION', 'PHOTOGRAPHY', 'PRODUCTIVITY', 'SHOPPING', 'SOCIAL', 'SPORTS', 'TOOLS',
                      'TRANSPORTATION', 'TRAVEL_AND_LOCAL', 'VIDEO_PLAYERS', 'WEATHER']
        for category in categories:
            self.geturl(category)
            self.spider()
            #break


if __name__ == '__main__':
    yyb = GooglePlay()
    yyb.start()
