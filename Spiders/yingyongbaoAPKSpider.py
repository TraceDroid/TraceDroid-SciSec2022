import re
import urllib.request
import os

       
class class_YYB:
    def __init__(self):
        self.urllist = []
        self.baseurl = 'https://android.myapp.com/myapp/category.htm?orgame=1&categoryId='

    def geturl(self, pageindex):
        for i in range(100, pageindex):
            self.urllist.append(self.baseurl+str(i))

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = response.readlines()
            link_list = []
            for i in range(len(html)):
                if 'ex_url' in str(html[i]):
                    tmp = str(html[i]).split('ex_url="')[1]
                    tmp = tmp.split('"')[0]
                    link_list.append(tmp)

            for url in link_list:
                file_name = url.split('=')[1]
                file_name = file_name.split('&')[0]
                load_path = "/data/yingyongbao/"
                os.chdir(load_path)
                # file_path = os.path.join("./tmp", file_name)
                # print("downloading:", file_name)
                file_path = load_path + file_name
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    urllib.request.urlretrieve(url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    continue

    def start(self):
        self.geturl(123)
        self.spider()
       
if __name__ == '__main__':
    yyb = class_YYB()
    yyb.start()