# -- coding: utf-8 --
# @Time: 2020/5/18 15:28
# @Author: liujianghua
# @Software: PyCharm
# @description:

import datetime
import dateparser
import sys
import os
import re
import zipfile


def zip_ya(startdir, file_news):
    startdir = startdir  #要压缩的文件夹路径
    file_news = startdir +'.zip' # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
            print('压缩成功')
    z.close()


if __name__ == '__main__':
    file_path = r'C:\Users\asus\Desktop\spiders'+'\\'
    for dirs in os.listdir(file_path):  # 获取文档内所有文件
        if os.path.isdir(file_path + dirs):
            zip_ya(os.path.join(file_path, dirs), dirs)
