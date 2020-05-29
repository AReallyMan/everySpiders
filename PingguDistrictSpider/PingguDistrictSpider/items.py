# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PinggudistrictspiderItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    source = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    publicTime = scrapy.Field()
    url = scrapy.Field()

    publicTimeStamp = scrapy.Field()
    # insertTime = scrapy.Field()
    # insertTimeStamp = scrapy.Field()
    #
    #
    #
    # sentiment = scrapy.Field()
    # spiderName = scrapy.Field()
    # spiderDesc = scrapy.Field()
    # siteType = scrapy.Field()
