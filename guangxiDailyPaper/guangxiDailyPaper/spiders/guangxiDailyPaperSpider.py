# @Time : 2020/5/28 9:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import GuangxidailypaperItem
from ..settings import ELASTICSEARCH_TYPE

# 广西日报
class GuangxidailypaperspiderSpider(CrawlSpider):
    name = 'guangxiDailyPaperSpider'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://gxrb.gxrb.com.cn/html/'+current_time+'/node_5.htm']
    rules = {
        Rule(LinkExtractor(allow='/'+current_time+'/node_\d+\.htm')),
        Rule(LinkExtractor(allow='/'+current_time+'/content_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = GuangxidailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//font[@color='#05006C']/h1/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='ozoom']/founder-content").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '广西日报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '广西日报'
            item['siteType'] = '纸媒'
            item['source'] = '广西日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

