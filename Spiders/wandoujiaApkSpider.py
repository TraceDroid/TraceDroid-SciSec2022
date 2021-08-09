import urllib

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

load_path = "/data/wandoujia/"
os.chdir(load_path)

#获取各个分类的url
data = requests.get('https://www.wandoujia.com/category/app')
s = BeautifulSoup(data.text, "html.parser")
divs = [li.div.find_all('a') for li in s.find_all('div')[4].find_all('ul')[0].find_all('li')]

urls_dict = {}
for i in range(len(divs)):
    #print(divs[i])
    for j in range(len(divs[i])):
        title = divs[i][j].attrs['title']
        url = divs[i][j].attrs['href']
        urls_dict[title] = url

#获取软件分类

base_url = 'https://www.wandoujia.com/wdjweb/api/category/more?catId='
apps = {}
apps_install = {}
for key in urls_dict.keys():
    # key = '视频'
    num = 1
    page_last = False
    catid = urls_dict[key].split('/')[4].split('_')[0]
    subCatId = urls_dict[key].split('/')[4].split('_')[1]

    while not page_last: #每个分类最后一页停止
        #拼接出每页的url，点击加载更多，page会增1
        url = 'https://www.wandoujia.com/wdjweb/api/category/more?catId={}&subCatId={}&page={}&ctoken=4Op4yfsiSsr8OAzRt5b1MtwE'.format(catid, subCatId, num)
        # print(url)
        #爬取对应的网页
        data = requests.get(url)
        #解析出json
        json = data.json()
        content = json['data']['content']
        if content != '':   #判断是否最后一页
            soup = BeautifulSoup(content, "html.parser")
            # print(soup)
            for li in soup.find_all('li'):
                package_name = str(li).split('data-pn="')[1]
                file_name = package_name.split('"')[0] + '.apk'
                file_path = load_path + file_name
                app_id = str(li).split('data-appid="')[1]
                app_id = app_id.split('"')[0]
                download_url = "https://www.wandoujia.com/apps/%s/download/dot?ch=detail_normal_dl" % app_id
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    continue

            num = num + 1
        else:
            #触发则表示当前分类已经加载所有页面，即到最后一页
            page_last = True
