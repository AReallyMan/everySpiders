# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
# from elasticsearch import Elasticsearch
# import elasticsearch.helpers
# from pymongo import MongoClient
# import redis
from scrapy.mail import MailSender
# #from kafka import KafkaProducer
# import json
# import os
# import sys
# path = [
#     "/usr/local/workspace-gerapy/gerapy/projects",
#     "D:/python_workspace",
#     '/app/spiders'
# ]
# [sys.path.append(p)for p in path if os.path.isdir(p)]
# from spider_util.duplicate import Duplicate #临时环境
# from spider_util.settings import *  # 公共配置
# from spider_util.sentimentAnalysis import SentimentAnalysis #情感分析
# from .settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
#
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
        body = '招标邮件，及时查收'
        subject = spider.output_excel_filename
        attach_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        f = open(spider.output_excel_filename, "rb")
        return mailer.send(to=["zhzwcs3@126.com"], subject=subject, body=body, cc=["zhzwx9@163.com"],
                           attachs=[(spider.output_excel_filename, attach_mime, f)], mimetype="text/plain", charset='utf-8')

class MiyundistrictspiderPipeline(object):
    def __init__(self):
        #self.file = open("json.json","wb")
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题','发布时间','公告内容','链接','发布时间戳','来源'])

    def process_item(self, item, spider):
        line = [item['title'], item['publicTime'], item['content'],item['url'],item['publicTimeStamp'],item['source']]
        self.ws.append(line)
        self.wb.save( spider.output_excel_filename)
        # sentiment = SentimentAnalysis()
        # item['sentiment'] = sentiment.analysis(item['title'])
        # item['spiderName'] = ELASTICSEARCH_TYPE
        # item['spiderDesc'] = '密云区'
        # item['siteType'] = '新闻'
        return item


