# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TencentItem(scrapy.Item):
    # define the fields for your item here like:
    PostId = scrapy.Field()
    PostName = scrapy.Field()
    CountryName = scrapy.Field()
    LocationName = scrapy.Field()
    BGName = scrapy.Field()
    CategoryName = scrapy.Field()
    Responsibility = scrapy.Field()
    LastUpdateTime = scrapy.Field()
    PostURL = scrapy.Field()
    Requirement = scrapy.Field()
