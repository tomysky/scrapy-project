# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from pymongo import MongoClient

class TencentPipeline:
    def open_spider(self,spider):
        client = MongoClient()
        self.collection = client['tencent']['post']

    def process_item(self, item, spider):
        new_item = {
            '职位id':item['PostId'],
            '职位名称':item['PostName'],
            '国家':item['CountryName'],
            '具体位置':item['LocationName'],
            'BG名':item['BGName'],
            '分类名':item['CategoryName'],
            '岗位职责':item['Responsibility'],
            '最近发布时间':item['LastUpdateTime'],
            '详细地址':item['PostURL'],
            '岗位需求': item['Requirement'],
        }
        self.collection.insert(new_item)
        return item