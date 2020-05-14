# -*- coding: utf-8 -*-
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import ShenzhentequpaperItem
from ..settings import ELASTICSEARCH_TYPE


# 深圳特区报
class ShenzhentequpaperspiderSpider(CrawlSpider):
    name = 'shenzhentequPaperSpider'
    allowed_domains = ['sztqb.sznews.com']
    current_time = time.strftime("%Y%m/%d")
    today = datetime.date.today()
    start_urls = ['http://sztqb.sznews.com/PC/layout/'+current_time+'/node_A01.html']
    rules = {
        Rule(LinkExtractor(allow='node_.*\.html')),
        Rule(LinkExtractor(allow='content_\d+\.html'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = ShenzhentequpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//div[@class='newsdetatit']/h3/text()").extract_first()
            if "广告" not in title:
                item['url'] = response.url
                item['title'] = title
                fromwhereAndPublishtime = response.xpath("//div[@class='newsdetatit']/p[3]/span[2]/text()").extract_first()
                item['fromwhere'] = '深圳特区报'
                item['publishtime'] = re.findall("\d+年\d+月\d+日", fromwhereAndPublishtime)[0]
                content = response.xpath("//div[@class='newsdetatext']/founder-content").xpath('string(.)').extract_first()
                if content:
                    content = re.findall("[\u4e00-\u9fa5]+", content);
                    item['content'] = ''.join(content)
                else:
                    item['content'] = ''
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '深圳特区报'
                item['siteType'] = '纸媒'
                item['source'] = '深圳特区报'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
