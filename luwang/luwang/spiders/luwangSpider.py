# @Time : 2020/5/25 14:07
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from ..items import LuwangItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..settings import ELASTICSEARCH_TYPE

# 鲁网
class LuwangspiderSpider(CrawlSpider):
    name = 'luwangSpider'
    # allowed_domains = ['sdnews.com.cn']
    start_urls = [ 'http://news.sdnews.com.cn/gn/', 'http://news.sdnews.com.cn/gj/']
    today = datetime.date.today()
    current_time = time.strftime("%Y%m%d", time.localtime())
    rules = {
        Rule(LinkExtractor(allow='index_\d\.htm')),
        Rule(LinkExtractor(allow='/'+current_time[0:6]+'/t'+current_time+'_\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = LuwangItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='fl endContent']/h1/text()").extract_first()
            item['editor'] = response.xpath("//div[@class='cc zrbj']/text()").extract_first()
            timeAndFrom = response.xpath("//div[@class='bb info']/span/text()").extract_first()
            if timeAndFrom:
                item['publishtime'] = re.findall("\d+-\d+-\d+ \d+:\d+", timeAndFrom)[0]
                item['fromwhere'] = re.findall("来源.*", timeAndFrom)[0]
            else:
                item['publishtime'] = ''
                item['fromwhere'] = ''
            content = response.xpath("//div[@class='TRS_Editor']").xpath('string(.)').extract_first()
            if content:
                content = re.findall("[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '鲁网'
            item['siteType'] = '新闻'
            item['source'] = '鲁网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
