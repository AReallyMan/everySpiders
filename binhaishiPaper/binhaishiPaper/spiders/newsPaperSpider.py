# -*- coding: utf-8 -*-

# @Time : 2020-06-04
# @Author : ZhangYangyang
# @Software: PyCharm
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import BinhaishipaperItem
from ..settings import ELASTICSEARCH_TYPE


# 滨海时报
class NewpaperSpider(CrawlSpider):
    name = 'newpaperSpider'
    current_time = time.strftime("%Y/%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.tjbhnews.com/finanec/', 'http://www.tjbhnews.com/life/',
                  'http://www.tjbhnews.com/xinwen/', 'http://bhsb.tjbhnews.com/']
    rules = {
        Rule(LinkExtractor(allow='/'+current_time+'/\d+\.html'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='/'+current_time+'/\d+_\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = BinhaishipaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
           print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='contTit']/font/text()").extract_first()
            editor = response.xpath("//div[@class='contTit']/font/text()").extract_first()
            if editor:
                item['editor'] = editor
            else:
                item['editor'] = ''
            item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            content = response.xpath("//div[@class='contTxt']/div").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//span[@id='source_baidu']/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '滨海时报'
            item['siteType'] = '纸媒'
            item['source'] = '滨海时报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
