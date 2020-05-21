# -*- coding: utf-8 -*-
import re

from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import NanchangeveningpaperItem
from ..settings import ELASTICSEARCH_TYPE


# 南昌晚报
class NanchangeveningpaperspiderSpider(CrawlSpider):
    name = 'nanchangEveningPaperSpider'
    allowed_domains = ['ncwbw.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['http://www.ncwbw.cn/html/'+current_time+'/node_9.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='http://www.ncwbw.cn/html/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = NanchangeveningpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            title = response.xpath("//td[@class='font01']/text()").extract_first()
            if title:
                item['title'] = title
                content = response.xpath("//div[@id='ozoom']").xpath('string(.)').extract_first()
                if content:
                    content = re.findall(u"[\u4e00-\u9fa5]+", content)
                    item['content'] = ''.join(content)
                item['publishtime'] = response.xpath("//span[@class='default']/strong/text()").extract_first()
                item['fromwhere'] = '南昌晚报'

                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '南昌晚报'
                item['siteType'] = '纸媒'
                item['source'] = '南昌晚报'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
