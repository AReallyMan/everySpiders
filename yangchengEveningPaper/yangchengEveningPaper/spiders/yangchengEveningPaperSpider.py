# -*- coding: utf-8 -*-
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import YangchengeveningpaperItem
from datetime import date, timedelta
from ..settings import ELASTICSEARCH_TYPE


# 羊城晚报
class YangchengeveningpaperspiderSpider(CrawlSpider):
    name = 'yangchengEveningPaperSpider'
    allowed_domains = ['ep.ycwb.com']
    # 16:00
    if 16 > time.localtime().tm_hour:
        print("羊城晚报尚未发布信息!此时为昨天的数据")
        current_time = (date.today() + timedelta(days = -1)).strftime("%Y-%m/%d")
    else:
        current_time = time.strftime("%Y-%m/%d")
    today = datetime.date.today()
    start_urls = ['http://ep.ycwb.com/epaper/ycwb/html/'+current_time+'/node_104.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='content_\d+_\d+\.htm'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = YangchengeveningpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//div[@class='article']/h1/text()").extract_first()
            if "A" not in title and "广告" not in title:
                item['url'] = response.url
                item['title'] = title
                item['fromwhere'] = response.xpath("//div[@class='info']/span[1]/text()").extract_first()
                item['author'] = response.xpath("//div[@class='info']/span[5]/text()").extract_first()
                item['publishtime'] = response.xpath("//div[@class='info']/span[2]/text()").extract_first()
                content = response.xpath("//div[@class='text']").xpath('string(.)').extract_first()
                if content:
                    content = re.findall("[\u4e00-\u9fa5]+", content);
                    item['content'] = ''.join(content)
                else:
                    item['content'] = ''
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '羊城晚报'
                item['siteType'] = '纸媒'
                item['source'] = '羊城晚报'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
