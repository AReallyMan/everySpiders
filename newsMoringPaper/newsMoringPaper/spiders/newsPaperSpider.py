# -*- coding: utf-8 -*-

# @Time : 2020-06-03 10:40:00
# @Author : ZhangYangyang
# @Software: PyCharm
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import NewsmoringpaperItem
from ..settings import ELASTICSEARCH_TYPE

# 新闻晨报
class NewpaperSpider(CrawlSpider):
    name = 'newsMoringPaper'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://epaper.zhoudaosh.com/html/' + current_time + '/node_3464.html']
    rules = {
        Rule(LinkExtractor(allow='/node_\d+\.html')),
        Rule(LinkExtractor(allow='content_\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = NewsmoringpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//p[@class='title1']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//td[@class='content_tt']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '新闻晨报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '新闻晨报'
            item['siteType'] = '纸媒'
            item['source'] = '新闻晨报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
