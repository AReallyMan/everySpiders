# -*- coding: utf-8 -*-
import scrapy
import datetime,time
import datetime as dt
from ..items import PinggudistrictspiderItem

class PinggudistrictSpider(scrapy.Spider):
    name = 'PingguDistrict'
    start_urls = ['http://www.bjpg.gov.cn/pgqrmzf/zwxx0/zfcg/index.html']
    zh_name = u'北京市平谷区人民政府'
    today = str(datetime.date.today())
    output_excel_filename = zh_name + '(' + today + ').xlsx'

    def parse(self, response):
        Listhref = response.xpath(
            ''' //div[@class = "ContentBoox"]//li/a[@target="_blank"]/@href''').extract()
        print(len(Listhref))
        for href in Listhref:
            # if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, href):
            #     print("该连接已被爬取")
            # else:
            href = "".join(href)
            href = "http://www.bjpg.gov.cn"+href
            print('1111', href)
            yield scrapy.Request(url=href, callback=self.detailpage)
        # 每页最后一个数据时间
        lasthreftime = response.xpath('''//div[@class = "ContentBoox"]//li[last()]/span/text()''').extract()[0]
        lasthreftime = "".join(lasthreftime).strip()
        print("*******", lasthreftime)
        todaytime = datetime.date.today()
        todaytime = str(todaytime)
        # 如果最后一个时间和当天时间相同 就跳转下页
        if lasthreftime == todaytime:
            nextpage  = response.xpath('''//div[@class="FenYe clearfix"]/p[@class="left"]/a[@title="下一页"]/@tagname ''').extract()[0]
            nextpage = 'http://www.bjpg.gov.cn' +nextpage
            yield scrapy.Request(url=nextpage, callback=self.parse)

    def detailpage(self, response):
        item = PinggudistrictspiderItem()
        title = response.xpath(
            '''  //div[@class="easysite-news-title"]/h2/text()''').extract()[0]
        title = "".join(title).strip()
        publicTimeSource = response.xpath(
            '''  //div[@class="easysite-news-title"]/p[@class="easysite-news-describe"]/text()[1]''').extract()[0]
        publicTimeSource = "".join(publicTimeSource).strip()
        publicTime = publicTimeSource[publicTimeSource.find('发布时间')+5:publicTimeSource.find('作者')]
        publicTime = "".join(publicTime).strip()
        publicTime = publicTime.replace('年','-').replace('月','-').replace('日','')
        publicTime = publicTime + ":00"
        source = publicTimeSource[publicTimeSource.find('来源') + 3:publicTimeSource.find('发布时间')]
        source = "".join(source).strip()
        author = publicTimeSource[publicTimeSource.find('作者') + 3:publicTimeSource.find('浏览量')]
        author = "".join(author).strip()
        # if author != "":
        #     author = author[author.find('记者') + 2:].strip()
        # # print("****",publicTime)
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
            ''' //div[@id="easysiteText"]/p//text()''').extract()
        content = "".join(content)
        if str(publicTime)[:10] == str(todaytime):
            item['title'] = title
            item['source'] = source
            item['author'] = author
            item['publicTime'] = publicTime
            item['content'] = content
            item['publicTimeStamp'] = publicTimeStamp
            # item['insertTime'] = insertTime
            # item['insertTimeStamp'] = insertTimeStamp
            item['url'] = response.url
            yield item
