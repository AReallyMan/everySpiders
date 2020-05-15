# -*- coding: utf-8 -*-
import datetime
import re
import time
from ..items import JiangxipaperItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..settings import ELASTICSEARCH_TYPE


# 江西日报
class JiangxipaperspiderSpider(CrawlSpider):
    name = 'jiangxiPaperSpider'
    # allowed_domains = ['jxnews.com.cn']
    start_urls = ['http://www.jxnews.com.cn/jxrb/']
    today = datetime.date.today()
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    rules = {
        Rule(LinkExtractor(allow='/system/'+current_time+'/\d+\.shtml'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = JiangxipaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//td[@class='title']/text()").extract_first()
            publishtime = response.xpath("//font[@color='#0000FF']/text()").extract_first()
            if publishtime:
                item['publishtime'] = re.findall("\d+-\d+-\d+ \d+:\d+", publishtime)[0]
            else:
                item['publishtime'] = ''
            content = response.xpath("//font[@id='Zoom']").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = "江西日报"
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '江西日报'
            item['siteType'] = '纸媒'
            item['source'] = '江西日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item