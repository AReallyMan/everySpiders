# @Time : 2020/5/27 10:00
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import ShandongbusinespaperItem
from ..settings import ELASTICSEARCH_TYPE

# 山东商报
class ShandongbusinesspiderSpider(CrawlSpider):
    name = 'shandongBusinesSpider'
    current_time = time.strftime("%Y-%#m/%#d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://readmeok.com/jdxw/', 'http://readmeok.com/xw/gnxw/', 'http://readmeok.com/xw/gjxw/',
                  'http://readmeok.com/xw/bdxw/']
    rules = {
        Rule(LinkExtractor(allow='default_\d\.htm')),
        Rule(LinkExtractor(allow='/'+current_time+'_\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = ShandongbusinespaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='endContent']/h1/text()").extract_first()
            timeAndFrom = response.xpath("//div[@class='info']/text()").extract_first()
            if timeAndFrom:
                item['fromwhere'] = re.findall(u"来源.*", timeAndFrom)[0]
                item['publishtime'] = re.findall("\d+-\d+-\d+ \d+:\d+:\d+", timeAndFrom)[0]
            else:
                item['fromwhere'] = ''
                item['publishtime'] = ''
            content = response.xpath("//div[@id='endText']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '山东商报'
            item['siteType'] = '纸媒'
            item['source'] = '山东商报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

