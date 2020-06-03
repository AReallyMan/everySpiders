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
from ..items import EverydayjingjinewsItem
from ..settings import ELASTICSEARCH_TYPE


# 每日经济新闻
class NewpaperSpider(CrawlSpider):
    name = 'everydayjingjinewsSpider'
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.nbd.com.cn/columns/3']
    rules = {
        Rule(LinkExtractor(allow='/page/[1-4]')),
        Rule(LinkExtractor(allow='http://www.nbd.com.cn/articles/' + current_time + '/\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = EverydayjingjinewsItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='g-article-top']/h1/text()[2]").extract_first()
            item['publishtime'] = response.xpath("//span[@class='time']/text()").extract_first()
            content = response.xpath("//div[@class='g-articl-text']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//span[@class='source']/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '每日经济新闻'
            item['siteType'] = '新闻'
            item['source'] = '每日经济新闻'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
