# -*- coding: utf-8 -*-
# @Time : 2020/5/25 17:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import QilueveningpaperItem
from ..settings import ELASTICSEARCH_TYPE

# 齐鲁晚报
class QilueveningpaperspiderSpider(CrawlSpider):
    name = 'qiluEveningPaperSpider'
    # allowed_domains = ['sjb.qlwb.com.cn']
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['https://sjb.qlwb.com.cn/qlwb/content/'+current_time+'/PageArticleIndexWZ.htm']
    rules = {
        Rule(LinkExtractor(allow='PageA\d+TB.htm')),
        Rule(LinkExtractor(allow='https://sjb.qlwb.com.cn/qlwb/content/'+current_time+'/[a-zA-Z\d]{15}\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = QilueveningpaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='zb']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//span[@id='contenttext']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//div[@class='nxx']/a/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '齐鲁晚报'
            item['siteType'] = '纸媒'
            item['source'] = '齐鲁晚报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
