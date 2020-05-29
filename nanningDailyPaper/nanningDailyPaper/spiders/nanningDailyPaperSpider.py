# @Time : 2020/5/21 15:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import NanningdailypaperItem
from ..settings import ELASTICSEARCH_TYPE

# 南宁日报
class NanningdailypaperspiderSpider(CrawlSpider):
    name = 'nanningDailyPaperSpider'
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.nnrb.com.cn/nnrb/'+current_time+'/html/index.htm']
    rules = {
        Rule(LinkExtractor(allow='page_\d+\.htm')),
        Rule(LinkExtractor(allow='/'+current_time+'/html/page_\d+_content_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = NanningdailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='bmnr_con_biaoti']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='zoom']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = '南宁日报'
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '南宁日报'
            item['siteType'] = '纸媒'
            item['source'] = '南宁日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item