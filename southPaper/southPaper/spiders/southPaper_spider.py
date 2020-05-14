# -*- coding: utf-8 -*-
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import SouthpaperItem
from ..settings import ELASTICSEARCH_TYPE


# 南方日报
class SouthpaperSpiderSpider(CrawlSpider):
    name = 'southPaper_spider'
    allowed_domains = ['epaper.southcn.com']
    current_time = time.strftime("%Y-%m/%d")
    today = datetime.date.today()
    start_urls = ['http://epaper.southcn.com/nfdaily/html/'+current_time+'/node_2.htm']
    rules = {
        Rule(LinkExtractor(allow='content_\d+\.htm'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = SouthpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['title'] = response.xpath("//div[@id='print_area']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='pub_time']/text()").extract_first()
            content = response.xpath("//div[@id='content']/founder-content").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content);
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '南方日报'
            item['siteType'] = '纸媒'
            item['source'] = '南方日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
