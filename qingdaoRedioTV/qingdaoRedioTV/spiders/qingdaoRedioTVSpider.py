# @Time : 2020/5/27 11:00
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import QingdaorediotvItem
from ..settings import ELASTICSEARCH_TYPE


# 青岛人民广播电台
class QingdaorediotvspiderSpider(CrawlSpider):
    name = 'qingdaoRedioTVSpider'
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://guangdian.qtv.com.cn/gddt/']
    rules = {
        Rule(LinkExtractor(allow='/system/'+current_time+'/\d+\.shtml'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = QingdaorediotvItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='content-l']/h1/text()").extract_first()

            item['fromwhere'] = response.xpath("//div[@class='news-resource']/span[2]/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='news-resource']/span[1]/text()").extract_first()

            content = response.xpath("//div[@class='news-content']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '青岛人民广播电台'
            item['siteType'] = '新闻'
            item['source'] = '青岛人民广播电台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
