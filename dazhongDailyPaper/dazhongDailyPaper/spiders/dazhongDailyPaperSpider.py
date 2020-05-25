# @Time : 2020/5/25 14:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import DazhongdailypaperItem
from ..settings import ELASTICSEARCH_TYPE


# 大众日报
class DazhongdailypaperspiderSpider(CrawlSpider):
    name = 'dazhongDailyPaperSpider'
    # allowed_domains = ['paper.dzwww.com']
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://paper.dzwww.com/dzrb/content/'+current_time+'/Page01NU.htm']
    rules = {
        Rule(LinkExtractor(allow='Page\d+NU.htm')),
        Rule(LinkExtractor(allow='http://paper.dzwww.com/dzrb/content/'+current_time+'/[a-zA-Z\d]+\.htm'), callback='parse_item')
    }

    def parse_item(self, response):
        item = DazhongdailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@id='news-header']/h1/text()").extract_first()
            item['editor'] = response.xpath("//div[@class='infor']/div/span[3]/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='infor']/div/span[1]/text()").extract_first()
            content = response.xpath("//span[@id='contenttext']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//div[@class='infor']/div/span[4]/text()[2]").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大众日报'
            item['siteType'] = '纸媒'
            item['source'] = '大众日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
