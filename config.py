# -*- coding: utf-8 -*-
# author: Kwinner Chen


import os


# 存储位置，改写需要绝对路径。
# 如果分割图片，分割后的图片存储在该位置下的cap文件夹下
POSITION = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'captcha\\')


# 任务线程数，用于下载验证码。改写需是一个正整数。
THREAD_NUM = os.cpu_count()


# 任务数量。由于图片验证码重复的问题，任务数量是保存到本地的图片的近似数量。
TASK_NUM = 200


# 网址，最后跟随的是一个0-1的随机数
URL = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&{0}'


# 用于图片分割
# 分割偏移量
DX = 73
DY = 73