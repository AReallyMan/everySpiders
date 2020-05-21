# @Time : 2020/5/21 15:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import QiluItem
from ..settings import ELASTICSEARCH_TYPE


# 齐鲁网
class QiluspiderSpider(CrawlSpider):
    name = 'qiluSpider'
    # allowed_domains = ['iqilu.com']
    current_time = time.strftime("%Y/%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://news.iqilu.com/shandong/yaowen/', 'http://news.iqilu.com/china/',
                  'http://news.iqilu.com/guoji/']
    rules = {
        Rule(LinkExtractor(allow='list_\d+_\d\.shtml')),
        Rule(LinkExtractor(allow=''+current_time+'/\d+\.shtml'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = QiluItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='section-cnt-tit clearfix']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//p[@class='time']/text()").extract_first()
            content = response.xpath("//div[@class='article-main']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//p[@class='resource']/span/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '齐鲁网'
            item['siteType'] = '新闻'
            item['source'] = '齐鲁网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
