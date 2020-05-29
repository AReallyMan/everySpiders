# @Time : 2020/5/26 10:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import JinandailypaperItem
from ..settings import ELASTICSEARCH_TYPE


#济南日报
class JinandailypaperspiderSpider(CrawlSpider):
    name = 'jinanDailyPaperSpider'
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://jnrb.e23.cn/']
    rules = {
        Rule(LinkExtractor(allow='/'+current_time+'/v\d+\.shtml')),
        Rule(LinkExtractor(allow='/'+current_time+'/\d+\.shtml'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = JinandailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='detail']/h2/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='p3']/text()").extract_first()
            content = response.xpath("//div[@class='article']/p/font").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '济南日报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '济南日报'
            item['siteType'] = '纸媒'
            item['source'] = '济南日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

