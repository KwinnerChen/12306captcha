#! /usr/bin/env python
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from PIL import Image
import os
import config


def _cut(im, p1, p2):
    box = p1 + p2
    imc = im.crop(box)
    return imc

def main(impath, dx=73, dy=73):
    '''impath:文件对象；
       dx：横轴偏移量；
       dy：纵轴偏移量；
       storage：分割的图片是否存储，默认不存储。
       返回一个字典，包括标题，1-8序号所对应的图片二进制对象
    '''
    path = os.path.join(config.POSITION, 'cap\\')
    
    if not os.path.isdir(path):
        os.mkdir(path)
    print('存储目录：%s' % path)
    
    im = Image.open(impath)
    l = im.size[0]  # 图片长
    w = im.size[1]  # 图片宽
    xs = 0  # 起始横坐标
    ys = 0  # 起始纵坐标
    tw = 30  # 标题宽度
    n = 1  # 分割次数
    
    while ys + tw + dy < w:
        while xs + dx < l:
            ims = _cut(im, (xs, ys+tw), (xs+dx, ys+tw+dy))
            xs += dx
            ims.save(r'%s%s_%s.jpg' % (path, os.path.basename(impath).split('.jpg')[0], n))
            n += 1
        xs = 0
        ys += dy


if __name__ == '__main__':
    l = (config.POSITION+'\\%s'%x for x in os.listdir(config.POSITION))
    for i in l:
        file_name = os.path.basename(i)
        try:
            print('分割%s' % file_name)
            main(i, config.DX, config.DY)
        except:
            print('%s无法分割。' % file_name)
        
