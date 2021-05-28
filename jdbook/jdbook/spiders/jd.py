# -*- coding: utf-8 -*-
import scrapy
import json
import re
from copy import deepcopy
from jdbook.items import JdbookItem

class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = ['https://pjapi.jd.com/book/sort?source=bookSort&callback=jsonp_1621398878974_14193']

    def start_requests(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Referer": "https://book.jd.com/booksort.html"
        }
        cookies = '__jdv=76161171|direct|-|none|-|1621369795721; __jdu=16213697957201608443211; areaId=19; ipLoc-djd=19-1607-4773-0; PCSYCityID=CN_440000_440300_440306; shshshfpa=fb7db170-1c16-3047-e1f6-1b56eccb4050-1621369797; shshshfpb=hEedtsvnuBooNjkjyj7P41Q%3D%3D; mt_xid=V2_52007VwMVUV1aVVIZQR1aBmYDFVNUXVdYHEkZbFBuBhMGX1EARktJHV4ZYgFAWkEIWwlIVR1eUW8AFFIPWAYKF3kaXQZnHxNWQVhaSx5NElkEbAYWYl9oUmoWSR9YDWIEE1BZXVVSH0oZXwxuMxJUWVw%3D; user-key=e8094a9c-ffa3-48e6-8709-a6bb176f56aa; shshshfp=2d92b8c9b79ff7591f0e016e9281ddae; _fbp=fb.1.1621386106091.1054287006; RT="z=1&dm=jd.com&si=3mxljaa3dk&ss=kourfpga&sl=1&tt=0&obo=1&ld=2v6&r=b6580f23e32046adf610b4d32aa006fe&ul=2v7&hd=2ve"; __jda=122270672.16213697957201608443211.1621369796.1621386105.1621397119.4; __jdc=122270672; 3AB9D23F7A4B3C9B=F5KTBS53KDESSFHBPTTWYGAS4NKHA6RNIHOMGFVTC7VT4SQV2LDZUBA6XPIEQMNVHHY7G6ELWSD56N6UXUAGX3GEE4; __jdb=122270672.5.16213697957201608443211|4.1621397119'
        cookies = {i.split("=")[0]:i.split("=")[1] for  i in cookies.split("; ")}
        yield scrapy.Request(url=self.start_urls[0],headers=headers,callback=self.parse,cookies=cookies)

    def parse(self, response):
        item = JdbookItem()
        # json_str = re.findall("jsonp_1621398878974_14193\((.*)\)", response.text)[0]
        # json_str = json.loads(json_str)
        # json_str = json.dumps(json_str,ensure_ascii=False)

        with open("jd.json","r",encoding='utf-8') as f:
            json_str = json.load(f)
        print("json : ",json_str)
        print(type(json_str))
        i = 0
        while True:
            try:
                item['big_cate'] = json_str['data'][i]['categoryName']
                print()
            except Exception as e:
                print(e)
                break
            item['big_cate_id'] = int(json_str['data'][i]['categoryId'])
            item['big_cate_id_father'] = int(json_str['data'][i]['fatherCategoryId'])
            print(item)
            j = 0
            while True:
                print(222)
                try:
                    item['small_cate'] = json_str['data'][i]['sonList'][j]['categoryName']
                except:
                    break
                item['small_cate_id'] = int(json_str['data'][i]['sonList'][j]['categoryId'])
                url = "https://list.jd.com/{}-{}-{}.html".format(str(item['big_cate_id_father']),str(item['big_cate_id']),str(item['small_cate_id']))
                item['url'] = url
                print(item)
                yield scrapy.Request(url=item['url'],callback=self.parse_list,meta={"item":deepcopy(item)})
                j += 1

            i += 1

    def parse_list(self,response):
        item = deepcopy(response.meta['item'])
        li_list = response.xpath("//div[@id='J_goodsList']/ul/li")
        for li in li_list:
            detail_href = response.xpath(".//div[@class='p-img']/a/@href").extract_first()
            if detail_href:
                detail_href = response.urljoin(detail_href.strip())
            else:
                detail_href = None
            item['detail_href'] = detail_href
            yield scrapy.Request(url=item['detail_href'],callback=self.parse_detail,meta={"item":deepcopy(item)})


        if 'cur_page' not in response.meta.keys():
            cur_page = 2
        else:
            cur_page = response.meta['cur_page']
        if cur_page <=100:
            cat = "{},{},{}".format(str(item['big_cate_id_father']),str(item['big_cate_id']),str(item['small_cate_id']))
            next_url ='https://list.jd.com/list.html?cat={}&page={}&click=0'.format(cat,str(cur_page))
            print("翻页了 ：",next_url)
            cur_page += 1
            yield scrapy.Request(url=next_url,callback=self.parse_list,meta={"item":response.meta['item'],'cur_page':cur_page})



    def parse_detail(self,response):
        item = response.meta['item']
        title = response.xpath("//div[@class='sku-name']//text()").extract_first()
        author = response.xpath("//div[@class='p-author']//text()").extract_first()
        if title:
            item['title'] =title.strip().decode('utf-8')
        else:
            item['title'] = None
        if author:
            item['author'] =author.strip().decode('utf-8')
        else:
            item['author'] = None
        cat = re.findall("cat: \[(\d+,\d+,\d+)\],",response.text)[0]
        skuId =re.findall("info\?skuId=(\d+)&",response.text)[0]
        base_url = 'https://item-soa.jd.com/getWareBusiness?skuId={}&cat={}'.format(skuId,cat)
        yield scrapy.Request(base_url,callback=self.parse_price,meta={"item":deepcopy(item)})

    def parse_price(self,response):
        item = response.meta['item']
        price =re.findall('"op":"(\d+\.\d+)",',response.text)[0]
        if price:
            price = price.strip()
        else:
            price = None
        item['price'] = price
        print(item)
        yield item