#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from proxyPool.IPPool import IPPool
from agentPool import User_Agent
from queue import Queue
from threading import Thread
from hashlib import md5
import config
import requests
import random
import os


def image_download(url, proxy, agent, q_r):  # proxy是python字典， agent为字符串
    try:
        header = {'User-Agent': agent}
        resp = requests.get(url, proxies=proxy, headers=header, timeout=5)
        resp.raise_for_status
        im = resp.content
        if len(im) > 3072:
            q_r.put(im)
            print('%s下载完成！\n' % url)
    except Exception as e:
        print('%s 下载出错：%s\n' % (url, e))


def storage(im_path, q_r):
    s = set()
    try:
        os.makedirs(im_path)
    except FileExistsError:
        pass
    while True:
        md = md5()
        r = q_r.get()
        if r is None:
            break
        md.update(r)
        md_r = md.hexdigest()  # 进行md5编码去重
        if md_r in s:
            continue
        # 生成一个8位的随机字符串作为文件名
        im_name = ''.join('%02X' % random.randint(0, 255) for i in range(4))
        im_name += '.jpg'
        with open(im_path+im_name, 'wb') as im:
            im.write(r)
        print('%s已存！\n' % im_name)
        q_r.task_done()


def worker(q_t, q_r, proxy_list, agent_list):
    while True:
        task = q_t.get()
        if task is None:
            break
        proxy = random.choice(proxy_list)
        agent = random.choice(agent_list)
        image_download(url=task, q_r=q_r, proxy=proxy, agent=agent)
        q_t.task_done()


if __name__ == '__main__':
    im_path = config.POSITION
    agent_list = User_Agent
    proxy_list = IPPool().get_ips
    q_t = Queue()
    q_r = Queue()
    thread_task_num = config.THREAD_NUM
    thread_list = []
    task_num = config.TASK_NUM
    url = config.URL

    for i in range(thread_task_num):  # 创建4个任务线程，并开始
        t = Thread(target=worker, args=(q_t, q_r, proxy_list, agent_list,))
        t.start()
        thread_list.append(t)
    t_s = Thread(target=storage, args=(im_path, q_r,))  # 创建一个结果存储线程，并开始
    t_s.start()
    thread_list.append(t_s)

    print('存储位置：%s' % im_path)

    for u in range(task_num):  # 添加任务
        q_t.put(url.format((str(random.random()))))
    q_t.join()  # 待所有下载任务完成
    print('任务下载完成')

    for n in range(thread_task_num):  # 添加任务终止信号
        q_t.put(None)

    q_r.join()  # 待所有存储任务完成
    q_r.put(None)  # 添加存储终止信号

    for s in thread_list:  # 等待所有线程结束
        s.join()
    print('验证码抓取完成！')
    input('任意键退出')
