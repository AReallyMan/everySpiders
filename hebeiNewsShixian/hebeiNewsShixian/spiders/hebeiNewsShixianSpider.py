# -*- coding: utf-8 -*-

# @Time : 2020-06-01 14:12:03
# @Author : ZhangYangyang
# @Software: PyCharm
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import HebeinewsshixianItem
from ..settings import ELASTICSEARCH_TYPE


# 河北新闻网市县
class HebeinewsshixianspiderSpider(CrawlSpider):
    name = 'hebeiNewsShixianSpider'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://sjz.hebnews.cn/node_73703.htm', 'http://cd.hebnews.cn/node_77285.htm',
                  'http://zjk.hebnews.cn/node_14345.htm', 'http://qhd.hebnews.cn/node_67091.htm',
                  'http://ts.hebnews.cn/node_22633.htm', 'http://ts.hebnews.cn/node_145014.htm',
                  'http://lf.hebnews.cn/node_83287.htm', 'http://www.hebnews.cn/node_355597.htm',
                  'http://bd.hebnews.cn/node_17051.htm', 'http://cangzhou.hebnews.cn/node_153180.htm',
                  'http://hs.hebnews.cn/node_24980.htm', 'http://world.hebnews.cn/node_152.htm']
    rules = {
        Rule(LinkExtractor(allow='/' + current_time + '/content_\d+\.htm'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = HebeinewsshixianItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='g_width content']/h1/text()").extract_first()
            item['editor'] = response.xpath("//div[@class='editor']/text()").extract_first()
            fromAndPublish = response.xpath("//div[@class='post_source']/text()").extract_first()
            if fromAndPublish:
                item['publishtime'] = re.findall("\d+-\d+-\d+ \d+:\d+:\d+", fromAndPublish)[0]
                item['fromwhere'] = re.findall("来源.*", fromAndPublish)[0]
            else:
                item['publishtime'] = ''
                item['fromwhere'] = ''
            content = response.xpath("//div[@class='text']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '河北新闻网市县'
            item['siteType'] = '新闻'
            item['source'] = '河北新闻网市县'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
