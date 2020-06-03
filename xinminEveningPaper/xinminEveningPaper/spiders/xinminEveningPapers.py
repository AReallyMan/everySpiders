# -*- coding: utf-8 -*-

# @Time : 2020-06-02 17:50:31
# @Author : ZhangYangyang
# @Software: PyCharm
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import XinmineveningpaperItem
from ..settings import ELASTICSEARCH_TYPE


# 新民晚报
class XinmineveningpapersSpider(CrawlSpider):
    name = 'xinminEveningPapers'
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['https://paper.xinmin.cn/html/xmwb/'+current_time+'/1.html']
    rules = {
        Rule(LinkExtractor(allow='/html/xmwb/'+current_time+'/\d+/\d+\.html')),
        Rule(LinkExtractor(allow='/html/xmwb/'+current_time+'/\d+/\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = XinmineveningpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//h2[@class='dzb-title-box']/text()").extract_first()
            item['editor'] = response.xpath("//span[@class='dzb-author-box']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@class='dzb-enter-desc-box dzb-enter-heng-desc-box']").xpath(
                'string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '新民晚报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '新民晚报'
            item['siteType'] = '新闻'
            item['source'] = '新民晚报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
