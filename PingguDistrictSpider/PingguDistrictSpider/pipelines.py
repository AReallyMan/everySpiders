# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
# from elasticsearch import Elasticsearch
from scrapy.mail import MailSender

import os
# import elasticsearch.helpers
# from pymongo import MongoClient
# import redis
# #from kafka import KafkaProducer
# import json
import os
import sys
path = [
    "/usr/local/workspace-gerapy/gerapy/projects",
    "D:/python_workspace",
    '/app/spiders',
    'C:\\Users\\asus\\Desktop\\spiders'
]
[sys.path.append(p)for p in path if os.path.isdir(p)]
from common_scrapy_pipeline import *
# from spider_util.duplicate import Duplicate #临时环境
# from spider_util.settings import *  # 公共配置
# from spider_util.sentimentAnalysis import SentimentAnalysis #情感分析
# from .settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE

# class MongoPipeline(object):
#     def open_spider(self, spider):
#         pass
#
#     def process_item(self, item, spider):
#         return item
#
#     def close_spider(self, spider):
#         pass
# class ElasticsearchPipeline(object):
#     def open_spider(self, spider):
#         self.es = Elasticsearch(([{"host": ELASTICSEARCH_HOST, "port": str(ELASTICSEARCH_PORT)}]))
#
#     def process_item(self, item, spider):
#         actions = [
#             {
#                 '_op_type': 'index',
#                 '_index': ELASTICSEARCH_INDEX,
#                 '_type': ELASTICSEARCH_TYPE,
#                 '_source': dict(item)
#             }
#         ]
#         elasticsearch.helpers.bulk(self.es, actions)  # 添加操作'''
#         return item
#
#     def close_spider(self, spider):
#         pass
#
# class RedisPipeline(object):
#     def open_spider(self, spider):
#         spider.duplicate = Duplicate(spider.name)
#         spider.duplicate.find_all_url(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_TYPE, source='url')
#
#     def process_item(self, item, spider):
#         return item
#
#     def close_spider(self, spider):
#         print('爬虫关闭')
#         r = redis.Redis(host=REDIS_HOST, port=str(REDIS_PORT), db=0)
#         r.delete(spider.name)

class EmailPipeline(object):
    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        mailer = MailSender(smtphost="smtp.163.com",
                            mailfrom="zhzwx9@163.com",
                            smtppass="FVDYFCDKVXGTVKNA",
                            smtpuser="zhzwx9@163.com",
                            smtpport=25,
                            smtptls=True
                            )

        subject = spider.output_excel_filename
        attach_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if os.path.isfile(spider.output_excel_filename):
            attachs = [(spider.output_excel_filename, attach_mime, open(spider.output_excel_filename, "rb"))]
            body = '招标邮件，及时查收'
        else:
            body = (spider.zh_name + '今日无数据('+spider.today+')').encode('utf-8')
            attachs = () #, "zhaorui@rietergroup.com"
        return mailer.send(to=["zhzwx9@163.com"], subject=subject, body=body, cc=["zhzwx9@163.com"],
                               attachs=attachs, mimetype="text/plain", charset='utf-8')


class PinggudistrictspiderPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题', '发布时间', '公告内容', '链接', '发布时间戳', '来源', '作者'])

    def process_item(self, item, spider):
        line = [item['title'], item['publicTime'], item['content'], item['url'], item['publicTimeStamp'],
                item['source'], item['author']]
        self.ws.append(line)
        self.wb.save(spider.output_excel_filename)
        return item


