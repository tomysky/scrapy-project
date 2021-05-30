import scrapy
from tencent.items import TencentItem
from copy import deepcopy
import time

class HrSpider(scrapy.Spider):
    name = 'hr'
    allowed_domains = ['tencent.com']
    start_urls = []
    #自定义第一次请求的api
    def start_requests(self):
        url = "https://careers.tencent.com/tencentcareer/api/post/Query?timestamp={}&countryId=1&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword=&pageIndex=1&pageSize=10&language=zh-cn&area=cn".format(str(int(time.time()*1000)))
        self.headers = {
            'authority': 'careers.tencent.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'referer': 'https://careers.tencent.com/search.html?query=co_1&index=2&sc=1'
        }

        yield scrapy.Request(url=url,callback=self.parse_list,headers=self.headers)

    def parse_list(self, response):
        item = TencentItem()
        post_list = response.json()['Data']['Posts']
        #解析json()数据
        for post in post_list:
            item['PostId'] = post['RecruitPostId']
            item['PostName'] = post['RecruitPostName']
            item['CountryName'] = post['CountryName']
            item['LocationName'] = post['LocationName']
            item['BGName'] = post['BGName']
            item['CategoryName'] = post['CategoryName']
            item['Responsibility'] = post['Responsibility'].replace("\n","")
            item['LastUpdateTime'] = post['LastUpdateTime']
            item['PostURL'] = post['PostURL']
            item['BGName'] = post['BGName']
            item['BGName'] = post['BGName']
            #解析详情页
            yield scrapy.Request(url=item['PostURL'],headers=self.headers,callback=self.parse_detail,meta={"item":deepcopy(item)})

        #翻页操作
        if response.meta.get("page",1)==1:
            response.meta["page"] = 2
        url = "https://careers.tencent.com/tencentcareer/api/post/Query?timestamp={}&countryId=1&cityId=&bgIds=&productId=&categoryId=&parentCategoryId=&attrId=&keyword=&pageIndex={}&pageSize=10&language=zh-cn&area=cn".format(str(int(time.time()*1000)),str(response.meta["page"]))
        print("第{}页:{}".format(str(response.meta["page"]),url))
        headers = {
            'authority': 'careers.tencent.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'referer': 'https://careers.tencent.com/search.html?query=co_1&index={}&sc=1'.format(str(response.meta["page"]-1))
        }
        next_url = response.meta["page"]+1
        #调用自己来解析
        yield  scrapy.Request(url=url,callback=self.parse_list,headers=headers,meta={"page":next_url})


    #解析详情页
    def parse_detail(self,response):
        item = response.meta['item']
        headers = {
            'authority': 'careers.tencent.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'referer': item['PostURL']
        }
        #拼接url，访问requirement
        url = "https://careers.tencent.com/tencentcareer/api/post/ByPostId?timestamp={}&postId={}&language=zh-cn".format(str(int(time.time()*1000)),item['PostId'])
        yield scrapy.Request(url=url,headers=headers,callback=self.parse_requirement,meta={"item":deepcopy(item)})

    #解析职位要求
    def parse_requirement(self,response):
        item = response.meta['item']
        item['Requirement'] = response.json()['Data']['Requirement'].replace("\n","")
        yield item
