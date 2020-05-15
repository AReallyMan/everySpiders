# -*- coding: utf-8 -*-
import json
import re
import time
from urllib import parse
import datetime
import scrapy
from ..items import ShenzhentvItem
from ..settings import ELASTICSEARCH_TYPE


# 深圳电视台
class ShenzhentvspiderSpider(scrapy.Spider):
    name = 'shenzhenTVSpider'
    # allowed_domains = ['sztv.cutv.com']
    start_urls = ['http://sztv.cutv.com/']
    today = datetime.date.today()
    basic_url = "https://api.scms.sztv.com.cn/api/com/article/getArticleList?"
    params = {
        "tenantId": "ysz",
        "catalogId": 9830,
        "page": 1,
        "banner": 1
    }

    def start_requests(self):
        params = self.params.copy()
        catalogId = [9830, 5352, 13366, 9155]
        for id in catalogId:
            params['catalogId'] = id
            for i in range(1, 10):
                params['page'] = i
                url = self.basic_url + parse.urlencode(params)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        JSONdata = response.text
        datas = json.loads(JSONdata)
        for datalist in datas['returnData']['news']:
            if str(datetime.date.today()) + " 00:00:00" < datalist['publishDate'] < str(
                    datetime.date.today()) + " 23:59:59":
                url, title, publishtime, author = datalist['url'], datalist['title'], datalist['publishDate'], datalist['addUser']
                item = ShenzhentvItem()
                item['title'] = title
                item['publishtime'] = publishtime
                item['author'] = author
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
            item['content'] = ''
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '深圳电视台'
        item['siteType'] = '新闻'
        item['source'] = '深圳电视台'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item