# @Time : 2020/5/26 14:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import QingdaodailypaperItem
from ..settings import ELASTICSEARCH_TYPE


# 青岛日报
class QingdaodailypaperspiderSpider(CrawlSpider):
    name = 'qingdaoDailyPaperSpider'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.dailyqd.com/news/node_3111.htm',
                  'http://www.dailyqd.com/news/node_3118.htm',
                  'http://www.dailyqd.com/news/node_3117.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+_\d\.htm')),
        Rule(LinkExtractor(allow='/'+current_time+'/content_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = QingdaodailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='articlebox']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='articlebox']/h2/span[1]/text()").extract_first()
            content = response.xpath("//div[@class='articlebox']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//div[@class='articlebox']/h2/span[2]/a/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '青岛日报'
            item['siteType'] = '纸媒'
            item['source'] = '青岛日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item