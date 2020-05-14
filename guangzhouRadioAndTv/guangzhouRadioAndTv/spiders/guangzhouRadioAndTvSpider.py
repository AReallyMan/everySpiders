# -*- coding: utf-8 -*-
import re
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import GuangzhouradioandtvItem
import time
import datetime
from ..settings import ELASTICSEARCH_TYPE


# 广州人民广播电台
class GuangzhouradioandtvspiderSpider(CrawlSpider):
    name = 'guangzhouRadioAndTvSpider'
    allowed_domains = ['dynamic.gztv.com']
    today = datetime.date.today()
    current_time = time.strftime("%Y%m/%d", time.localtime())
    start_urls = ['https://dynamic.gztv.com/domInfo/gnzxc','https://dynamic.gztv.com/interInfo/gwzxc']
    rules = {
        Rule(LinkExtractor(allow='https://dynamic.gztv.com/a/'+current_time+'/[a-zA-Z0-9]+\.html'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = GuangzhouradioandtvItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//span[@id='story_title']/text()").extract_first()
            if title:
                item['title'] = title
                item['publishtime'] = response.xpath("//span[@class='u10751_text2']/text()").extract_first()
                content = response.xpath("//div[@id='Content']").xpath('string(.)').extract_first()
                if content:
                    content = re.findall(u"[\u4e00-\u9fa5]+", content)
                    item['content'] = ''.join(content)
                else:
                    item['content'] = ''
                item['fromwhere'] = response.xpath("//span[@class='u10751_text1']/text()").extract_first()
                item['url'] = url
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '广州人民广播电台'
                item['siteType'] = '新闻'
                item['source'] = '广州人民广播电台'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
