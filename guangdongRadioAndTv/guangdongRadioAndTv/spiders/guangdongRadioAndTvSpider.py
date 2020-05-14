# -*- coding: utf-8 -*-
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import GuangdongradioandtvItem
from ..settings import ELASTICSEARCH_TYPE


# 广东广播电视台
class GuangdongradioandtvspiderSpider(CrawlSpider):
    name = 'guangdongRadioAndTvSpider'
    allowed_domains = ['gdtv.cn']
    current_time = time.strftime("%Y-%m-%d")
    today = datetime.date.today()
    start_urls = ['http://www.gdtv.cn/index/rollnews/']
    rules = {
        Rule(LinkExtractor(allow='index_\d\.html')),
        Rule(LinkExtractor(allow='http://www.gdtv.cn/index/rollnews/'+current_time+'/\d+\.html'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = GuangdongradioandtvItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='article-title pull-left']/h1/text()").extract_first()
            item['url'] = response.url
            item['fromwhere'] = response.xpath("//span[@class='article-assist']/span[1]/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='article-assist']/span[2]/text()").extract_first()
            content = response.xpath("//div[@class='article-main']").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '广东广播电视台'
            item['siteType'] = '新闻'
            item['source'] = '广东广播电视台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
