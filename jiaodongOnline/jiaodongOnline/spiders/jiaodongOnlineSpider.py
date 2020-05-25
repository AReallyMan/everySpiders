# @Time : 2020/5/22 13:28
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import JiaodongonlineItem
from ..settings import ELASTICSEARCH_TYPE


# 胶东在线
class JiaodongonlinespiderSpider(CrawlSpider):
    name = 'jiaodongOnlineSpider'
    allowed_domains = ['jiaodong.net']
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.jiaodong.net/news/china/shizheng/', 'http://www.jiaodong.net/news/world/',
                  'http://www.jiaodong.net/news/sd/']
    rules = {
        Rule(LinkExtractor(allow='/'+current_time+'/\d+\.shtml'), callback='parse_item')
    }

    def parse_item(self, response):
        item = JiaodongonlineItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//div[@class='millia']/h1/text()").extract_first()
            if title:
                item['title'] = title
            elif response.xpath("//div[@id='conTit']/h1/text()[1]").extract_first():
                title = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//div[@id='conTit']/h1/text()[1]").extract_first())
                item['title'] = ''.join(title)
            elif response.xpath("//h2[@id='activity-name']/text()").extract_first():
                title = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//h2[@id='activity-name']/text()").extract_first())
                item['title'] = ''.join(title)
            else:
                item['title'] = ''
            editor = response.xpath("//div[@class='f12 lh26 tr pt40 pb40']/text()").extract_first()
            if editor:
                item['editor'] = editor
            elif response.xpath("//div[@class='edit']/text()").extract_first():
                item['editor'] = response.xpath("//div[@class='edit']/text()").extract_first()
            else:
                item['editor'] = ''
            publishtime = response.xpath("//div[@class='source f14']/text()[1]").extract_first()
            if publishtime:
                item['publishtime'] = re.findall("\d+-\d+-\d+ .*", publishtime)[0]
            elif response.xpath("//span[@class='h-time']/span/text()").extract_first():
                item['publishtime'] = response.xpath("//span[@class='h-time']/span/text()").extract_first()
            else:
                item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='content']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            elif response.xpath("//div[@id='js_content']").xpath('string(.)').extract_first():
                content = re.findall(u"[\u4e00-\u9fa5]+", response.xpath("//div[@id='js_content']").xpath('string(.)').extract_first())
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            fromwhere = response.xpath("//div[@class='source f14']/text()[1]").extract_first()
            if fromwhere:
                item['fromwhere'] = re.findall(u"[\u4e00-\u9fa5]+", fromwhere)[1]
            elif response.xpath("//em[@id='source']/text()").extract_first():
                item['fromwhere'] = response.xpath("//em[@id='source']/text()").extract_first()
            else:
                item['fromwhere'] = response.xpath("//a[@id='js_name']/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '胶东在线'
            item['siteType'] = '新闻'
            item['source'] = '胶东在线'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
