# -*- coding: utf-8 -*-
import re

from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import NanchangdailypaperItem
from ..settings import ELASTICSEARCH_TYPE


# 南昌日报
class NanchangdailypaperspiderSpider(CrawlSpider):
    name = 'nanchangDailyPaperSpider'
    allowed_domains = ['ncrbw.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['http://www.ncrbw.cn/html/'+current_time+'/node_1.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='http://www.ncrbw.cn/html/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = NanchangdailypaperItem()
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
                item['fromwhere'] = '南昌日报'

                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '南昌日报'
                item['siteType'] = '纸媒'
                item['source'] = '南昌日报'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
