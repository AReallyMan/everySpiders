# -*- coding: utf-8 -*-

# @Time : 2020-06-01 10:21:09
# @Author : ZhangYangyang
# @Software: PyCharm
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import ShijiazhuangchannelItem
from ..settings import ELASTICSEARCH_TYPE


# 河北长城网(长城网下的区市)
class ShijiazhuangchannelspiderSpider(CrawlSpider):
    name = 'shijiazhuangChannelSpider'
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://sjz.hebei.com.cn/sjzyw/index.shtml', 'http://sjz.hebei.com.cn/sjzxw/index.shtml',
                  'http://sjz.hebei.com.cn/sjzgs/index.shtml', 'http://sjz.hebei.com.cn/jjsh/index.shtml',
                  'http://cd.hebei.com.cn/cdxw/', 'http://zjk.hebei.com.cn/zjkxw/index.shtml',
                  'http://qhd.hebei.com.cn/jrxw/index.shtml', 'http://qhd.hebei.com.cn/xqxw/index.shtml',
                  'http://ts.hebei.com.cn/tgz/jryw/index.shtml', 'http://ts.hebei.com.cn/rxw/index.shtml',
                  'http://lf.hebei.com.cn/lfxw/qxdt/index.shtml', 'http://bd.hebei.com.cn/gnxw/',
                  'http://bd.hebei.com.cn/gjxw/', 'http://bd.hebei.com.cn/hbxw/',
                  'http://cz.hebei.com.cn/scxw/index.shtml', 'http://hs.hebei.com.cn/jrjj/index.shtml',
                  'http://xt.hebei.com.cn/ncyw/index.shtml', 'http://hd.hebei.com.cn/hdyw/',
                  'http://dingzhou.hebei.com.cn/dzkx/index.shtml',
                  ]
    rules = {
        Rule(LinkExtractor(allow='/system/'+current_time+'/\d+\.shtml'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = ShijiazhuangchannelItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='g_width content']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='post_source']/text()[2]").extract_first()
            content = response.xpath("//div[@class='text']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                item['content'] = ''
            item['fromwhere'] = response.xpath("//div[@class='post_source']/text()[1]").extract_first().split("作者")[0]
            item['editor'] = response.xpath("//div[@class='post_source']/text()[1]").extract_first().split("作者")[1]
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '长城网'
            item['siteType'] = '新闻'
            item['source'] = '长城网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

