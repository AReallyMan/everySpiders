# -*- coding: utf-8 -*-
# @Time : 2020/5/21 16:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import DazhongItem
from ..settings import ELASTICSEARCH_TYPE


# 大众网
class DazhongspiderSpider(CrawlSpider):
    name = 'dazhongSpider'
    allowed_domains = ['dzwww.com']
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.dzwww.com/xinwen/guoneixinwen/', 'http://www.dzwww.com/xinwen/guojixinwen/',
                  'http://www.dzwww.com/xinwen/shehuixinwen/']
    rules = {
        Rule(LinkExtractor(allow='default_\d\.htm')),
        Rule(LinkExtractor(allow=''+current_time[0:6]+'/t'+current_time+'_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = DazhongItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@id='news-head']/h2/text()").extract_first()
            publishtime = response.xpath("//div[@class='date']/label/text()").extract_first()
            item['publishtime'] = str(self.today) + " " + publishtime
            content = response.xpath("//div[@id='news-body']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            author = response.xpath("//div[@class='text'][2]/p/text()").extract_first()
            if author:
                item['author'] = author
            else:
                item['author'] = ''
            item['fromwhere'] = response.xpath("//div[@id='news-side']/div[@class='text'][1]/p/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大众网'
            item['siteType'] = '新闻'
            item['source'] = '大众网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item