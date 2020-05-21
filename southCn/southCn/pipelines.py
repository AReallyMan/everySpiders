# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from openpyxl import Workbook
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import redis
from kafka import KafkaProducer
import json

from redis import Redis

from .settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import os
import sys
path = [
  "/usr/local/workspace-gerapy/gerapy/projects", "C:/Users/asus/Desktop/spiders", "/app/spiders"
]
[sys.path.append(p)for p in path if os.path.isdir(p)]
from spider_util.duplicate import Duplicate  # 临时环境
from spider_util.settings import *  # 公共配置


class SouthcnPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['时间', '来源', '标题', '内容', '链接', '作者'])

    def process_item(self, item, spider):
        line = [item['publishtime'], item['fromwhere'], item['title'], item['content'],
                item['url'], item['editor']]
        self.ws.append(line)
        self.wb.save(r"南方网.xlsx")
        return item


class KafkaPipeline(object):
    def open_spider(self, spider):
        self.producer = KafkaProducer(bootstrap_servers=['sentiment01:9092', 'sentiment03:9092'],
                                      value_serializer=lambda m: json.dumps(m).encode('ascii'))

    def process_item(self, item, spider):
        item['index'] = ELASTICSEARCH_INDEX
        self.producer.send('sentiment', dict(item))
        return item

    def close_spider(self, spider):
        self.producer.flush()
        self.producer.close()


class MongoPipeline(object):
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://192.168.1.51:27017/")
        mydb = myclient["portia"]
        self.mycol = mydb["sites"]

    def process_item(self, item, spider):
        self.mycol.insert_one(dict(item))


class ElasticsearchPipeline(object):
    def open_spider(self, spider):
        self.es = Elasticsearch(([{"host": ELASTICSEARCH_HOST, "port": str(ELASTICSEARCH_PORT)}]))

    def process_item(self, item, spider):
        actions = [
            {
            '_op_type': 'index',
            '_index': ELASTICSEARCH_INDEX,
            '_type': ELASTICSEARCH_TYPE,
            '_source': dict(item)
            }
        ]
        elasticsearch.helpers.bulk(self.es, actions)  # 添加操作'''
        return item

    def close_spider(self, spider):
        pass


class RedisPipeline(object):
    def open_spider(self, spider):
        spider.duplicate = Duplicate(spider.name)
        spider.duplicate.find_all_url(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_TYPE, source='url')

    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        print('爬虫关闭')
        r = redis.Redis(host=REDIS_HOST, port=str(REDIS_PORT), db=0)
        r.delete(spider.name)


class Duplicate(object):

    def __init__(self, dbName='dupe'):
        self.redis_db = Redis(host=REDIS_HOST, port=str(REDIS_PORT), db=0)  # 连接redis
        self.redis_data_dict = dbName  # 存储所有url的key

    def find_all_url(self, index, doc_type, source):
        # 查询所有的url
        es = Elasticsearch([{"host": ELASTICSEARCH_HOST, "port": str(ELASTICSEARCH_PORT)}])

        queryData = es.search(index=index,
                              doc_type=doc_type,
                              scroll='5m',
                              timeout='3s',
                              size=100,
                              body={"query": {"match_all": {}}},
                              _source=source)

        mdata = queryData.get("hits").get("hits")

        if not mdata:
            print('empty!')
        else:
            for i in mdata:
                # 把每一条的值写入key的字段里
                self.redis_db.hset(self.redis_data_dict, i["_source"][source], 0)
            scroll_id = queryData["_scroll_id"]
            total = queryData["hits"]["total"]

            for i in range(int(total / 100)):
                res = es.scroll(scroll_id=scroll_id, scroll='5m')  # scroll参数必须指定否则会报错
                for j in res["hits"]["hits"]:
                    # 把每一条的值写入key的字段里
                    if source in j["_source"].keys():
                        self.redis_db.hset(self.redis_data_dict, j["_source"][source], 0)





