# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JdbookItem(scrapy.Item):
    # define the fields for your item here like:
    big_cate = scrapy.Field()
    big_cate_id = scrapy.Field()
    big_cate_id_father = scrapy.Field()
    small_cate = scrapy.Field()
    small_cate_id = scrapy.Field()
    url = scrapy.Field()
    detail_href = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
