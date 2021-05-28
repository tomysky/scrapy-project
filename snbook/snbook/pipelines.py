# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient

class Snbook2Pipeline:
    def open_spider(self,spider):
        client = MongoClient()
        self.collection = client['subook']['books']

    def process_item(self, item, spider):
        new_item = {
            '标题':item['title'],
            '作者':item['author'],
            '大分类':item['big_cate'],
            '小分类':item['small_cate'],
            '详细分类':item['detail_cate'],
            '详细分类地址':item['detail_cate_href'],
            '发布时间':item['publish_time'],
            '发行社':item['publish'],
            '详细地址':item['detail_href'],
            '价格':item['price'],
        }



        self.collection.insert(new_item)
        print('*' * 50)
        print(item['title'],' ok!  ')
        print(new_item)
        print('*'*50)
        return item