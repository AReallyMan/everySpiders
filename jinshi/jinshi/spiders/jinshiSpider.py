# -*- coding: utf-8 -*-
import datetime
import json
import re
import time
from urllib import parse
from ..items import JinshiItem
import scrapy
from ..settings import ELASTICSEARCH_TYPE


# 今视网
class JinshispiderSpider(scrapy.Spider):
    name = 'jinshiSpider'
    allowed_domains = ['jxntv.cn']
    start_urls = ['http://jxntv.cn/']
    today = datetime.date.today()
    basic_url = "http://app.jxntv.cn/tagnews.php?"
    params = {
        "catid[]": 45,
        "pg": 1,
        "datatype": "json"

    }

    def start_requests(self):
        params = self.params.copy()
        catalogId = [45, 61, 160, 159]
        for id in catalogId:
            params['catid[]'] = id
            for i in range(1, 10):
                params['pg'] = i
                url = self.basic_url + parse.urlencode(params)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        JSONdata = response.text
        datas = json.loads(JSONdata)
        for data in datas:
            item = JinshiItem()
            now = datetime.datetime.now()
            # 今日0点
            zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                                 microseconds=now.microsecond)
            # 今日23点59
            lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
            zerostamp = int(time.mktime(time.strptime(str(zeroToday), "%Y-%m-%d %H:%M:%S")))
            laststamp = int(time.mktime(time.strptime(str(lastToday), "%Y-%m-%d %H:%M:%S")))
            if zerostamp < int(data['published']) < laststamp:
                title, url = data['title'], data['url']
                item['title'] = title
                item['url'] = url
                if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                    print("该连接已被爬取")
                else:
                    yield scrapy.Request(url=url, meta={"item": item}, callback=self.getDetail)

    def getDetail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='content']").xpath('string(.)').extract_first()
        if content:
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
        else:
            item['content'] = '图片或者视频'

        editor = response.xpath("//span[@class='editor']/text()").extract_first()
        if editor:
            item['editor'] = editor
        else:
            item['editor'] =''
        item['publishtime'] = response.xpath("//span[@class='date']/text()").extract_first()
        item['fromwhere'] = response.xpath("//span[@class='source']/text()").extract_first()
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '今视网'
        item['siteType'] = '新闻'
        item['source'] = '今视网'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item


