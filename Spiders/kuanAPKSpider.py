import requests
import queue
import threading
import re
import os
from lxml import etree
from copy import deepcopy
import urllib.request


session = requests.session()


class KuAn(object):

    def __init__(self, type, page):
        self.type = type
        self.page = page
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        self.url = 'https://www.coolapk.com'
        self.base_url = 'https://www.coolapk.com/{}'.format(type)
        if type not in ['apk', 'game']:
            raise ValueError('type参数不在范围内')
        self.page_url_queue = queue.Queue()
        self.detail_url_queue = queue.Queue()
        self.save_queue = queue.Queue()

    def get_detail_url_fun(self):
        while True:
            page_url = self.page_url_queue.get()
            req = session.get(url=page_url, headers=self.header)
            if req.status_code == 200:
                req.encoding = req.apparent_encoding
                html = etree.HTML(req.text)
                path = html.xpath('//*[@class="app_left_list"]/a/@href')
                for _ in path:
                    detail_url = self.url + _
                    # print('正在获取详情链接:',detail_url)
                    self.detail_url_queue.put(deepcopy(detail_url))
            self.page_url_queue.task_done()

    def get_download_url_fun(self):
        while True:
            detail_url = self.detail_url_queue.get()
            req = session.get(url=detail_url, headers=self.header)
            if req.status_code == 200:
                req.encoding = 'utf-8'
                url_reg = 'href=(.*?)&from=click'
                name_reg = 'pn=(.*?)&'
                download_url = re.findall(url_reg, req.text)[0]
                # print(download_url)
                name = re.findall(name_reg, download_url)[0]
                download_url = download_url[1:] + "&from=click"
                data = {'name': name, 'url': download_url}
                # print(download_url)
                # print(name)
                file_name = name + '.apk'
                load_path = "/data/kuan/"
                file_path = load_path + file_name
                os.chdir(load_path)
                try:
                    if os.path.exists(file_path):
                        print("apk exists")
                        continue
                    response = session.get(download_url)
                    with open(file_name, "wb") as code:
                        code.write(response.content)
                    # urllib.request.urlretrieve(download_url, file_name)
                    print("downloading success")
                except Exception as e:
                    print("download failed")
                    continue


                # print('获取到数据:', data)
                self.save_queue.put(data)
            self.detail_url_queue.task_done()

    # def save_data_fun(self):
    #     pass
    #     while True:
    #         data = self.save_queue.get()
    #         name = data.get('name')
    #         url = data.get('url')
    #         urllib.request.urlretrieve(url, name)



    def run(self):
        for _ in range(1, self.page+1):
            page_url = self.base_url + '?p={}'.format(_)
            # print('下发页面url', page_url)
            self.page_url_queue.put(page_url)

        thread_list = []
        for _ in range(2):
            get_detail_url = threading.Thread(target=self.get_detail_url_fun)
            thread_list.append(get_detail_url)

        for _ in range(5):
            get_download_url = threading.Thread(target=self.get_download_url_fun)
            thread_list.append(get_download_url)

        # for _ in range(2):
        #     save_data = threading.Thread(target=self.save_data_fun)
        #     thread_list.append(save_data)

        for t in thread_list:
            t.setDaemon(True)
            t.start()

        for q in [self.page_url_queue, self.detail_url_queue, self.save_queue]:
            q.join()

        print('爬取完成，结束')

if __name__ == '__main__':

    a= KuAn(type='apk', page=302).run()
