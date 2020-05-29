import datetime
import json
import re
import time
from urllib import parse
from ..items import GuangxinewsItem
import scrapy
from ..settings import ELASTICSEARCH_TYPE


# 广西新闻网
class GuangxinewsspiderSpider(scrapy.Spider):
    name = 'guangxiNewsSpider'
    start_urls = ['http://jxntv.cn/']
    today = datetime.date.today()
    basic_url = "https://v.gxnews.com.cn/index.php?"
    params = {
        "c": "www",
        "a": "getArticles",
        "sortids": 21659,
        "start": 0

    }

    def start_requests(self):
        params = self.params.copy()
        for i in range(0, 400, 20):
            params['start'] = i
            url = self.basic_url + parse.urlencode(params)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        JSONdata = response.text
        datas = json.loads(JSONdata)
        for data in datas:
            item = GuangxinewsItem()
            now = datetime.datetime.now()
            # 今日0点
            zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                                 microseconds=now.microsecond)
            # 今日23点59
            lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
            zerostamp = int(time.mktime(time.strptime(str(zeroToday), "%Y-%m-%d %H:%M:%S")))
            laststamp = int(time.mktime(time.strptime(str(lastToday), "%Y-%m-%d %H:%M:%S")))
            if zerostamp < int(data['date']) < laststamp:
                title, url, editor, source, publishtime = data['title'], data['url'], data['editor'], data['source'], data['date_ymdhis']
                item['title'] = title
                item['url'] = url
                item['editor'] = editor
                item['fromwhere'] = source
                item['publishtime'] = publishtime
                if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                    print("该连接已被爬取")
                else:
                    yield scrapy.Request(url=url, meta={"item": item}, callback=self.getDetail)

    def getDetail(self, response):
        item = response.meta['item']
        content = response.xpath("//div[@class='article-content']").xpath('string(.)').extract_first()
        if content:
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
        else:
            item['content'] = ''
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '广西新闻网'
        item['siteType'] = '新闻'
        item['source'] = '广西新闻网'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item
