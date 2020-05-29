# @Time : 2020/5/29 14:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import GuangxipeoplerediotvItem
from ..settings import ELASTICSEARCH_TYPE


# 广西人民广播电台
class GuangxipeoplerediotvspiderSpider(CrawlSpider):
    name = 'guangxiPeopleRedioTVSpider'
    current_time = time.strftime("%Y/%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.bbrtv.com/Simplified/news/radio/',
                  'http://www.bbrtv.com/Simplified/news/hotnews/',
                  'http://www.bbrtv.com/Simplified/news/gxnews/',
                  'http://www.bbrtv.com/Simplified/news/Domestic/',
                  'http://www.bbrtv.com/Simplified/news/world/']
    rules = {
        Rule(LinkExtractor(allow='radio/\d\.html')),
        Rule(LinkExtractor(allow='/'+current_time+'/\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = GuangxipeoplerediotvItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='main z']/h1/text()").extract_first()
            item['editor'] = response.xpath("//div[@class='inf']/span[3]/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='inf']/span[2]/text()").extract_first()
            content = response.xpath("//div[@class='content']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//div[@class='inf']/span[1]/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '广西人民广播电台'
            item['siteType'] = '新闻'
            item['source'] = '广西人民广播电台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item