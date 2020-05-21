# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
from ..items import ZhongxinjwItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scrapy.mail import MailSender


class ZhongxinjwSpiderSpider(CrawlSpider):
    name = 'zhongxinjw_spider'
    #allowed_domains = ['chinanews.com']
    start_urls = ['http://www.jwview.com/znh.html', 'http://www.jwview.com/hg.html', 'http://www.jwview.com/jr.html', 'http://www.jwview.com/zq.html', 'http://www.jwview.com/sj.html', 'http://www.jwview.com/kj.html']
    current_time = time.strftime("%m-%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='http://www.jwview.com/jingwei/html/'+current_time+'/\d{6}\.shtml'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = ZhongxinjwItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='title']/h1/text()").extract_first()

            publishtime = response.xpath("//div[@class='title']/div/text()").extract_first()
            if publishtime:
                item['publishtime'] = publishtime[0:20]
            else:
                item['publishtime'] = ''
            fromwhere = response.xpath("//div[@class='title']/div/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere[20:]
            else:
                item['fromwhere'] = ''
            item['content'] = response.xpath("//div[@class='content_zw bgwhite']").xpath('string(.)').extract_first()

            item['editor'] = response.xpath("//div[@class='editor']/text()").extract_first()

            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中新经纬'
            item['siteType'] = '资讯'
            item['source'] = '中新经纬'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item




