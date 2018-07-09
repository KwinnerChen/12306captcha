#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


import time
import requests, re, random, os
from threading import Thread
from queue import Queue, Empty


class IPPool():
    '''一个小型IP池，十几个可用的HTTP代理，实例化时可以自行更换源地址（可能需要更改一下提取规则）。
       主要提供两个方法，get_ip()和get_ips()，前者随机返回一个HTTP代理的字典，形式类似于：
       {'http':'http://host:port'}
       后者返回一个字典的列表。所有IP数据在更换了源地址或者每30分钟自动更新一次。'''
    default_url = 'http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip'
    def __init__(self, url = default_url):
        self.headers = {'User-Agent':'Mozilla/5.0'}
        self.url = url
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IP.txt')

    def _page_downloader(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            html = response.text
            return html
        except:
            print('代理IP提取链接已失效，请更换链接！')
            return

    def _page_parse(self, html):    #提取页面IP信息，可能需要更改split（）参数
        if html:
            try:
                html_list = html.split('<br />')
                for html_cut in html_list:
                    if html_cut:
                        ip = re.search(r'((25[0-5]|2[0-4]\d|1\d{2}|\d?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|\d?\d):\d+', html_cut)
                        if ip:
                            yield ip.group()
            except:
                print('此页面没有可提取到的IP地址！请检查链接是否是代理界面链接')
                return
        else:
            print('链接不可用！')
            return

    def _ip_test(self, ip):    #用于测试提取的IP保证代理可用
        proxies_ip = {'http':'http://%s' % ip}
        try:
            rep = requests.get('http://www.baidu.com', proxies=proxies_ip, timeout=5)
            if rep.status_code == 200:
                return True
        except:
            return False

    def _tested_queue(self, ip, q):    # 多线程加快测试速度
        if self._ip_test(ip):
            q.put(ip)
            return
        else:
            return

    def _storage(self, q, f):
        while True:
            try:
                f.write(q.get(timeout=3)+'\n')
            except (Empty,ValueError):
                return

    def _refresh(self):    #刷新IP文档，存储通过测试的IP
        q = Queue()
        with open(self.file_path, 'w') as f:
            html = self._page_downloader()
            ip_generator = self._page_parse(html)
            t1 = Thread(target=self._storage, args=(q, f))
            t1.start()
            for ip in ip_generator:
                t = Thread(target=self._tested_queue, args=(ip, q))
                t.start()
            t1.join()
        print('更新完成！')

    @property
    def get_ip(self):
        '''返回为一个类似{'http':'http://1.2.3.4:5'}的字典'''

        if self.url != IPPool.default_url:
            print('源地址改变更新代理IP！')
            self._refresh()
            with open(self.file_path, 'r') as f:
                ips_list = f.readlines()
                return {'http':'http://%s' % random.choice(ips_list).strip()}
        elif os.path.isfile(self.file_path) and os.path.getsize(self.file_path) and int(time.time()-os.path.getmtime(self.file_path))<1800:
            with open(self.file_path, 'r') as f:
                ips_list = f.readlines()
                return {'http':'http://%s' % random.choice(ips_list).strip()}
        else:
            print('正在更新代理IP！')
            self._refresh()
            while True:
                if os.path.isfile(self.file_path) and os.path.getsize(self.file_path):
                    with open(self.file_path, 'r') as f:
                        ips_list = f.readlines()
                        return {'http':'http://%s' % random.choice(ips_list).strip()}

    @property
    def get_ips(self):
        '''返回一个如{'http':'http://1.2.3.4:5'}字典列表'''

        ips_list = []
        if self.url != IPPool.default_url:
            print('源地址改变，正在更新代理IP！')
            self._refresh()
            with open(self.file_path, 'r') as f:
                ip_list = f.readlines()
                for ip in ip_list:
                    ips_list.append({'http': 'http://%s' % ip.strip()})
                    return ips_list
        elif os.path.isfile(self.file_path) and os.path.getsize(self.file_path) and int(time.time()-os.path.getmtime(self.file_path))<1800:
            with open(self.file_path, 'r') as f:
                ip_list = f.readlines()
                for ip in ip_list:
                    ips_list.append({'http':'http://%s'%ip.strip()})
                return ips_list
        else:
            print('正在更新代理IP！')
            self._refresh()
            while True:
                if os.path.isfile(self.file_path) and os.path.getsize(self.file_path):
                    with open(self.file_path, 'r') as f:
                        ip_list = f.readlines()
                        for ip in ip_list:
                            ips_list.append({'http':'http://%s' % ip.strip()})
                        return ips_list
if __name__ == '__main__':
    ip = IPPool()
    proxy = ip.get_ip
    if proxy:
        print(proxy)
    input()
