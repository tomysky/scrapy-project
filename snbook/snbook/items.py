# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Snbook2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    big_cate = scrapy.Field()
    small_cate = scrapy.Field()
    detail_cate = scrapy.Field()
    detail_cate_href = scrapy.Field()
    author = scrapy.Field()
    publish = scrapy.Field()
    publish_time = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    detail_href = scrapy.Field()
    page_info = scrapy.Field()
