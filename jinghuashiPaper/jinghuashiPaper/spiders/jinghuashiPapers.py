# -*- coding: utf-8 -*-

# @Time : 2020-06-02 11:48:09
# @Author : ZhangYangyang
# @Software: PyCharm
import json

import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import JinghuashipaperItem
from ..settings import ELASTICSEARCH_TYPE


# 京华时报
class JinghuashipapersSpider(scrapy.Spider):
    name = 'jinghuashiPapers'
    today = datetime.date.today()
    start_urls = ['http://news.people.com.cn/210801/211150/index.js?_=1591073752225']

    def parse(self, response):
        JsonDatas = json.loads(response.text)
        for datalist in JsonDatas['items']:
            if str(datetime.date.today()) + " 00:00:00" < datalist['date'] < str(
                    datetime.date.today()) + " 23:59:59":
                url, title, publishtime = datalist['url'], datalist['title'], datalist['date']
                item = JinghuashipaperItem()
                item['title'] = title
                item['publishtime'] = publishtime
                item['url'] = url
                if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                    print("该连接已被爬取")
                else:
                    yield scrapy.Request(url=url, meta={"item": item}, callback=self.getDetail)

    def getDetail(self, response):
        item = response.meta['item']
        fromwhere = response.xpath("//p[@class='sou']/a/text()").extract_first()
        if fromwhere:
            item['fromwhere'] = fromwhere
        elif response.xpath("//div[@class='box01']/div/a/text()").extract_first():
            item['fromwhere'] = response.xpath("//div[@class='box01']/div/a/text()").extract_first()
        elif response.xpath("//div[@class='artOri']/a/text()").extract_first():
            item['fromwhere'] = response.xpath("//div[@class='artOri']/a/text()").extract_first()
        else:
            item['fromwhere'] = ''
        content = response.xpath("//div[@id='rwb_zw']").xpath('string(.)').extract_first()
        if content:
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
        elif response.xpath("//div[@id='rwb_zw']").xpath('string(.)').extract_first():
            content = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//div[@id='rwb_zw']").xpath('string(.)').extract_first())
            item['content'] = ''.join(content)
        elif response.xpath("//div[@class='artDet']").xpath('string(.)').extract_first():
            content = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//div[@class='artDet']").xpath('string(.)').extract_first())
            item['content'] = ''.join(content)
        else:
            item['content'] = ''
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '京华时报'
        item['siteType'] = '纸媒'
        item['source'] = '京华时报'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item