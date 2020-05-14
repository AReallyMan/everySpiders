# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
import os
import sys
path = [
    "/usr/local/workspace-gerapy/gerapy/projects",
    "E:/python1111/spider_project_yy"
]
[sys.path.append(p)for p in path if os.path.isdir(p)]


class BjwbPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['出处', '标题', '内容', '时间', '链接',  '版次', '作者'])

    def process_item(self, item, spider):
        line = [item['fromwhere'], item['title'], item['content'], item['timetoday'], item['url'], item['version'], item['auther']]
        self.ws.append(line)  # 以行的形式存储
        self.wb.save(r"北京晚报.xlsx")
        return item


