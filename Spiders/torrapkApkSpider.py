import re
import requests
import urllib.request
import os
from bs4 import BeautifulSoup

load_path = "/data/torrapk/"
os.chdir(load_path)

class fdroid:
    def __init__(self, category):
        self.urllist = []
        self.baseurl = 'https://www.torrapk.com/en/apps/{}/'.format(category)

    def geturl(self, pages):
        self.urllist.append(self.baseurl)
        for i in range(1, pages):
            self.urllist.append(self.baseurl + 'index-page-{}/'.format(i))
            # print(self.baseurl + '{}/index.html'.format(i))

    def spider(self):
        for i in range(len(self.urllist)):
            #header = {}
            #header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(i)
            #req = urllib.request.Request(self.urllist[i], headers=header)
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('div', class_='iconCont toolTip')
            for j in range(len(html)):
                tmp = str(html[j]).split('href="')[1]
                tmp = tmp.split('"')[0]
                app_value = tmp.split(self.baseurl)[1]
                app_value = app_value.split('-')[0]
                file_name = app_value + '.apk'
                #header = {}
                #header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(app_value)
                #req = urllib.request.Request(tmp, heders=header)
                messages = urllib.request.urlopen(tmp)
                detail = BeautifulSoup(messages, 'html.parser')
                detail_url = detail.find_all('div', class_='scoreVal staff')
                latest_link = str(detail_url).split('href="/')[1]
                latest_link = "https://www.torrapk.com/" + latest_link.split('"')[0]
                #header = {}
                #header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/{} Firefox/21.0'.format(file_name)
                #req = urllib.request.Request(latest_link, headers=header)
                download_link = urllib.request.urlopen(latest_link)
                download_res = BeautifulSoup(download_link, 'html.parser')
                download_tmp = download_res.find_all('form', name_='dwnld_form')
                download_tmp_new = str(download_tmp).split('value="')[1]
                vc_value = download_tmp_new.split('"')[0]
                download_url = latest_link + "?VC=" + vc_value + "&action=Download"
                # print(download_url)

                # print(file_name)
                file_path = load_path + file_name
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    #response = requests.get(download_url, headers=header, stream=True)
                    #with open(file_name, "wb") as code:
                    #    code.write(response.content)
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
        '25-antivirus': 3,
        '20-audio-media-and-video': 17,
        '22-tools-and-personalization': 28,
        '48-casual': 15,
        '17-games-and-entertainment': 90,
        '21-social-and-communication': 10,
        '23-news-and-magazines': 6,
        '24-office-and-productivity': 9,
        '19-photography': 22,
        '53-writing-drawing-and-painting': 2,
        '30-rooted-phones': 2,
        '35-shopping': 3,
        '36-sport-and-health': 7,
        '32-kids': 5,
        '29-travel': 6,
        '27-web-browser': 2,
        '37-emulators': 2,
        '54-education': 4,
        '38-cards-and-casino': 3,
        '45-medical': 2,
        '46-engineering-and-science': 2,
        '47-lifestyle': 5,
        '26-books-and-reference': 9,
        '51-sport-games': 3,
        '13-other': 5,
        '28-bank-and-finance': 3,
        '31-christmas': 2,
    }

    for category, pages in categories_pages.items():
        yyb = fdroid(category)
        yyb.start(pages)