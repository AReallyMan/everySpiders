# -*- coding: utf-8 -*-
import datetime
import re
import time
from ..settings import ELASTICSEARCH_TYPE
from scrapy.spiders import Rule, CrawlSpider
from ..items import GuangzhoupaperItem
from scrapy.linkextractors import LinkExtractor


# 广州日报
class GuangzhoupaperspiderSpider(CrawlSpider):
    name = 'guangzhouPaperSpider'
    allowed_domains = ['gzdaily.dayoo.com']
    current_time = time.strftime("%Y-%m/%d")
    today = datetime.date.today()
    start_urls = ['https://gzdaily.dayoo.com/pc/html/'+current_time+'/node_1.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='content_\d+_\d+\.htm'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = GuangzhoupaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//p[@class='BSHARE_TEXT']/text()").extract_first()
            if "广告" not in title or "声明" not in title or "公告" not in title:
                item['url'] = response.url
                item['title'] = title
                content = response.xpath("//div[@id='ozoom']/founder-content").xpath('string(.)').extract_first()
                if content:
                    content = re.findall("[\u4e00-\u9fa5]+", content);
                    item['content'] = ''.join(content)
                else:
                    item['content'] = ''
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '广州日报'
                item['siteType'] = '纸媒'
                item['source'] = '广州日报'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item

