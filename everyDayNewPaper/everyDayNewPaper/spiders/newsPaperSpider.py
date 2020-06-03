# -*- coding: utf-8 -*-

# @Time : 2020-06-03
# @Author : ZhangYangyang
# @Software: PyCharm
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import EverydaynewpaperItem
from ..settings import ELASTICSEARCH_TYPE


# 每日新报
class NewpaperSpider(CrawlSpider):
    name = 'newpaperSpider'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://epaper.tianjinwe.com/mrxb/mrxb/'+current_time+'/node_132.htm']
    rules = {
        Rule(LinkExtractor(allow='/node_\d+\.htm')),
        Rule(LinkExtractor(allow='content_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = EverydaynewpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
           print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//td[@class='font01']/text()").extract_first()
            editor = response.xpath("//td[@class='font02']/text()").extract_first()
            if editor:
                item['editor'] = editor
            else:
                item['editor'] = ''
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='ozoom']/founder-content").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '每日新报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '每日新报'
            item['siteType'] = '新闻'
            item['source'] = '每日新报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
