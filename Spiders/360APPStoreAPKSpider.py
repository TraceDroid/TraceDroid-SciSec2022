import re
import urllib.request
import os

class class_360:
    def __init__(self,category):
        self.urllist = []
        self.baseurl = 'http://zhushou.360.cn/list/index/cid/{}/?page='.format(category)

    def geturl(self, pageindex):
        for i in range(1, pageindex):
            self.urllist.append(self.baseurl+str(i))

    def spider(self):
        for i in range(len(self.urllist)):
            response = urllib.request.urlopen(self.urllist[i])
            html = str(response.read())
            # print(html)
            # print("get html")
            # link_list = re.findall(r"(?<=&url=).*?apk", html)
            link_list = re.findall(r'(?<=&url=).*?apk"', html)
            for url in link_list:
                # print(url)
                url = url[:-1]
                # print(url)
                file_name = url.split('?')[0]
                # print(file_name)
                file_name = file_name.split('/')[-1]
                # print(file_name)
                # file_path = os.path.join("./tmp", file_name)
                # print("downloading:", file_name)
                load_path = "/data/360/"
                os.chdir(load_path)
                # print(os.getcwd())
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
        self.geturl(50)
        # print("geturl success")
        self.spider()
        # print("spider success")
             
if __name__ == '__main__':
    category_list = [11, 12, 14, 15, 16, 18, 17, 102228, 102230, 102231, 102232, 102139, 102233]
    for category in category_list:
        a = class_360(category)
        a.start()
