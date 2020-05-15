# -*- coding: utf-8 -*-
import datetime
import re
import time
from ..items import ChinajiangxiItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..settings import ELASTICSEARCH_TYPE


# 中国江西网
class ChinajiangxispiderSpider(CrawlSpider):
    name = 'chinaJiangxiSpider'
    # allowed_domains = ['jxcn.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    start_urls = ['http://ce.jxcn.cn/hot/', 'http://jiangxi.jxnews.com.cn/lead/',
                  'http://jiangxi.jxnews.com.cn/society/', 'http://jiangxi.jxnews.com.cn/st_e_c_e/',
                  'http://jiangxi.jxnews.com.cn/economy/', 'http://jiangxi.jxnews.com.cn/p_e_/',
                  'http://www.jxcn.cn/jxnews/']
    rules = {
        Rule(LinkExtractor(allow='/system/'+current_time+'/\d+\.shtml'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ChinajiangxiItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//div[@class='title']/text()").extract_first()
            if title:
                item['title'] = title
            elif response.xpath("//span[@class='p22Bold']/text()").extract_first():
                item['title'] = response.xpath("//span[@class='p22Bold']/text()").extract_first()
            else:
                item['title'] = response.xpath("//div[@class='biaoti1']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            content = response.xpath("//font[@id='Zoom']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
            elif response.xpath("//td[@class='p14 cBlack']").xpath('string(.)').extract_first():
                content = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//td[@class='p14 cBlack']").xpath('string(.)').extract_first())
            else:
                content = response.xpath("//div[@id='fontzoom']").xpath('string(.)').extract_first()
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            fromwhere = response.xpath("//span[@id='source_baidu']/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = response.xpath("//td[@class='p12 cQBrown']/text()").extract_first()
            if response.xpath("//span[@id='source_baidu']/a/text()").extract_first():
                item['fromwhere'] = response.xpath("//span[@id='source_baidu']/a/text()").extract_first()
            item['editor'] = response.xpath("//span[@id='editor_baidu']/text()").extract_first()
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国江西网'
            item['siteType'] = '新闻'
            item['source'] = '中国江西网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
