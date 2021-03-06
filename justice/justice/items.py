# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JusticeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    publishtime = scrapy.Field()
    author = scrapy.Field()
    editor = scrapy.Field()
    fromwhere = scrapy.Field()
    url = scrapy.Field()
    content =scrapy.Field()

    spiderName = scrapy.Field()
    spiderDesc = scrapy.Field()
    siteType = scrapy.Field()
    source = scrapy.Field()
    publicTimeStamp = scrapy.Field()
    insertTimeStamp = scrapy.Field()
    index = scrapy.Field()
