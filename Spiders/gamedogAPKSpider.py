import re
import urllib.request
import os

       
class gamedog:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'http://www.gamedog.cn/android/list_soft_0_0_0_0_hot_%d.html'

    def geturl(self):
        for i in range(1, 24):
            self.urllist.append(self.baseurl % i)


    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = response.readlines()
            link_list = []
            for i in range(len(html)):
                if '_blank' in str(html[i]) and '<a' in str(html[i]):
                    tmp = str(html[i]).split('android/')[1]
                    tmp = tmp.split('.html')[0]
                    download_url = "http://m.gamedog.cn/downs/index/?id=" + tmp
                    load_path = "/data/gamedog/"
                    os.chdir(load_path)
                    file_name = tmp + '.apk'
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
        self.geturl()
        self.spider()
       
if __name__ == '__main__':
    yyb = gamedog()
    yyb.start()