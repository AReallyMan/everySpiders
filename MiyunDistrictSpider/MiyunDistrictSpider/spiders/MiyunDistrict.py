# -*- coding: utf-8 -*-
import scrapy
import datetime,time
import datetime,time
import datetime as dt
import re
from ..items import MiyundistrictspiderItem


class MiyundistrictSpider(scrapy.Spider):
    name = 'MiyunDistrict'
    start_urls = ['http://www.bjmy.gov.cn/col/col4082/index.html']
    zh_name = u'北京市密云区人民政府'
    today = str(datetime.date.today())
    output_excel_filename = zh_name + '(' + today + ').xlsx'
    page = 1
    def parse(self, response):
        results = re.findall(r'<li><a target="_blank" href=\"(?P<detailUrl>.*)\" title="(?P<title>.*)">.*</a><span>(?P<date>20\d{2}-\d{2}-\d{2})</span></li>', response.text)
        print(results)
        for result in results:
            detailUrl = result[0]
            # title     = result[1]
            # date      = result[2]
            # if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, detailUrl):
            #     print("该连接已被爬取")
            # else:
            print('----------',detailUrl)
            yield scrapy.Request(url=detailUrl, callback=self.detailpage)

        # print(len(result))
        lastresult = result[-1]
        lasthreftime = lastresult[2]
        todaytime = datetime.date.today()
        todaytime = str(todaytime)
        if lasthreftime[:10] == todaytime:
            self.page += 1
            nextpage = "http://www.bjmy.gov.cn/col/col4082/index.html?uid=838&pageNum="+self.page
            yield scrapy.Request(url=nextpage, callback=self.parse)

    def detailpage(self, response):
        item = MiyundistrictspiderItem()
        title = response.xpath(
            '''//div[@class="wz_tit"]/text()[2]''').extract()[0]
        title = "".join(title).strip()
        publicTime = response.xpath(
            '''//ul[@class="wz_sakl"]/li[2]/text()''').extract()[0]
        publicTime = "".join(publicTime).strip()
        publicTime = publicTime[publicTime.find('发布时间')+5:].strip()
        source = response.xpath('''//ul[@class="wz_sakl"]/li[1]/text()''').extract()[0]
        source = "".join(source).strip()
        source = source[source.find('来源')+3:]
        # print("****",publicTime)
        todaytime = datetime.date.today()
        # 发布时间如果为空 发布时间戳也设置为空
        if publicTime == '':
            publicTimeStamp = ''
        if publicTime != '':
            if len(publicTime) != 19:
                publicTime = publicTime + ":00"
            timeArray = time.strptime(str(publicTime), "%Y-%m-%d %H:%M:%S")
            # 拿到发布的时间戳
            publicTimeStamp = int(time.mktime(timeArray))
        # 拿到插入时间
        insertTime = dt.datetime.now().strftime('%F %T')
        # 拿到插入时间十三位时间戳
        insertTimeStamp = int(round(time.time() * 1000))
        # 只返回当天的数据
        content = response.xpath(
            '''//div[@id="ArticleContent"]//p//text() | //div[@class = "wz_article"]/p//text()''').extract()
        content = "".join(content)
        if str(publicTime)[:10] == str(todaytime):
            item['title'] = title
            item['source'] = source
            item['publicTime'] = publicTime
            item['content'] = content
            item['publicTimeStamp'] = publicTimeStamp
            # item['insertTime'] = insertTime
            # item['insertTimeStamp'] = insertTimeStamp
            # item['comments'] = comments
            item['url'] = response.url
            yield item
