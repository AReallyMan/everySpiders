# -*- coding: utf-8 -*-
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import GreatriverItem
from ..settings import ELASTICSEARCH_TYPE


# 大江网
class GreatriverspiderSpider(CrawlSpider):
    name = 'greatRiverSpider'
    # allowed_domains = ['jxnews.com.cn']
    current_time = time.strftime("%Y/%m/%d")
    today = datetime.date.today()
    start_urls = ['http://news.jxnews.com.cn/gn/', 'http://news.jxnews.com.cn/szjj/',
                  'http://jiangxi.jxnews.com.cn/original/', 'http://news.jxnews.com.cn/cjxw/']
    rules = {
        Rule(LinkExtractor(allow='/system/'+current_time+'/\d+\.shtml'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = GreatriverItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='title']/text()").extract_first()
            item['url'] = response.url
            item['fromwhere'] = response.xpath("//span[@id='source_baidu']/text()").extract_first()
            item['editor'] = response.xpath("//span[@id='editor_baidu']/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            content = response.xpath("//font[@class='test1']").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ""
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大江网'
            item['siteType'] = '新闻'
            item['source'] = '大江网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
