# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import ChinashandongItem
import time
from ..settings import  ELASTICSEARCH_TYPE
import datetime


# 中国山东网
class ChinashandongspiderSpider(scrapy.Spider):
    name = 'chinaShanDongSpider'
    allowed_domains = ['news.sdchina.com']
    start_urls = ['http://news.sdchina.com/list/1228_1.html', 'http://news.sdchina.com/list/1751_1.html',
                  'http://news.sdchina.com/list/2215_1.html', 'http://news.sdchina.com/list/1227_1.html']
    today = datetime.date.today()
    current_time = time.strftime("%Y%m%d", time.localtime())
    page = 1

    def parse(self, response):
        flag = 0
        nodes = response.xpath("//div[@class='zleftb']/ul/li")
        for node in nodes:
            flag += 1
            publishtime = node.xpath("./div[@class='ztime']/span/text()").extract_first()
            if str(datetime.date.today()) == re.findall("\d+-\d+-\d+", publishtime)[0]:
                yield scrapy.Request(url=node.xpath("./p/a/@href").extract_first(), callback=self.getList)
            else:
                break
            if flag == 12:
                self.page += 1
                url = response.url.split("_")[0] + "_" + str(self.page) + "." + response.url.split("_")[1].split(".")[1]
                yield scrapy.Request(url=url, callback=self.parse)

    def getList(self, response):
        item = ChinashandongItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['editor'] = response.xpath("//div[@class='zleftg']/text()").extract_first()
            title = response.xpath("//div[@class='zzleft']/h1/text()").extract_first()
            if title:
                item['title'] = title
            else:
                item['title'] = ''
            timeAndFrom = response.xpath("//div[@class='zleftc']/text()").extract_first()
            if timeAndFrom:
                item['publishtime'] = re.findall("\d+/\d/\d+ \d+:\d+:\d+", timeAndFrom)[0]
                item['fromwhere'] = re.findall("来源.*", timeAndFrom)[0]
            else:
                item['publishtime'] = ''
                item['fromwhere'] = ''
            content = response.xpath("//div[@class='zleftf']").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国山东网'
            item['siteType'] = '资讯'
            item['source'] = '中国山东网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

