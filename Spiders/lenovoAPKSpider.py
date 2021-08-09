import re
import urllib.request
import os
from bs4 import BeautifulSoup
import string

load_path = "/data/lenovo/"
os.chdir(load_path)
       
class lenovo:
    def __init__(self):
        self.urllist = []
        self.baseurl = ''
    

    def geturl(self, category, id):
        for i in range(1, 22):
            self.baseurl = 'https://www.lenovomm.com/apps/{}/0?p={}&type='.format(category, i)
            self.urllist.append(self.baseurl + str(id))
            # print(self.baseurl + str(id))

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'item')
            link_list = []
            for j in range(len(html)):
                if 'appdetail' in str(html[j]):
                    tmp = str(html[j]).split('><img')[0][:-1]
                    tmp = tmp.split('href="')[1]
                    tmp = tmp.split('cateName')[0]
                    detail_url = "https://www.lenovomm.com" + tmp

                    file_name = tmp.split('/')[2] + '.apk'
                    file_path = load_path + file_name

                    detail = urllib.request.urlopen(detail_url)
                    download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='download')
                    download_url = str(download_url).split('href="')[1]
                    download_url = download_url.split('">')[0]
                    try:
                        if os.path.exists(file_path):
                            print("apk exists")
                            continue
                        urllib.request.urlretrieve(download_url, file_name)
                        print("downloading success")
                    except Exception as e:
                        print("download failed")
                        continue
        
    def spider2(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = BeautifulSoup(response, 'html.parser')
            html = html.find_all('a', class_ = 'item')
            link_list = []
            for j in range(len(html)):
                if 'appdetail' in str(html[j]):
                    tmp = str(html[j]).split('><img')[0][:-1]
                    tmp = tmp.split('href="')[1]
                    tmp = tmp.split('cateName')[0]
                    detail_url = "https://www.lenovomm.com" + tmp

                    file_name = tmp.split('/')[2] + '.apk'
                    file_path = load_path + file_name

                    detail = urllib.request.urlopen(detail_url)
                    apk_size = BeautifulSoup(detail, 'html.parser').find('span', class_='dec')
                    apk_size = str(apk_size).split('<!-- -->')[1]
                    if apk_size[-2] == 'M' and int(apk_size[:-2].split('.')[0]) < 300:
                        print(apk_size)
                        detail = urllib.request.urlopen(detail_url)
                        download_url = BeautifulSoup(detail, 'html.parser').find('a', class_='download')
                        # print(download_url)
                        download_url = str(download_url).split('href="')[1]
                        download_url = download_url.split('">')[0]
                        try:
                            if os.path.exists(file_path):
                                print("apk exists")
                                continue
                            urllib.request.urlretrieve(download_url, file_name)
                            print("downloading success")
                        except Exception as e:
                            print("download failed")
                            continue


    def start1(self, category):
        self.geturl(category, 1)
        self.spider()
    
    def start2(self, category):
        self.geturl(category, 2)
        self.spider2()

       
if __name__ == '__main__':

    app_category = [1038, 1028, 1030, 1034, 1052, 1048, 1040, 2351, 1042, 1060, 1046, 1058, 1062, 1032, 1054, 2441, 2461, 2463]
    game_category = [2367, 2393, 2373, 2383, 2395, 2389, 2481, 2501, 2521]
    for x in app_category:    
        yyb = lenovo()
        yyb.start1(x)
    
    for y in game_category:
        yyb = lenovo()
        yyb.start2(y)       