import scrapy
from snbook2.items import Snbook2Item
from copy import deepcopy
import re
import time

class SuSpider(scrapy.Spider):
    name = 'su'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
        item = Snbook2Item()
        div_list = response.xpath("//div[@class='menu-item']")
        div_list2 = response.xpath("//div[@class='menu-sub']")
        for index,div in enumerate(div_list):
            big_cate = div.xpath(".//h3/a/text()").extract_first()
            if big_cate:
                item['big_cate'] = big_cate.strip()
            print("big_cate : ",item['big_cate'])
            div3_list = div_list2[index].xpath("./div[1]")
            for div in div3_list:
                small_cate_a = div.xpath("./p//a/text()").extract()
                small_cate_ul = div.xpath("./ul")
                for index,a in enumerate(small_cate_a):
                    small_cate = a
                    print("small_cate : ",small_cate)
                    if small_cate:
                        item['small_cate'] = small_cate.strip()
                    detail_cate_li = small_cate_ul[index].xpath("./li")
                    for li in detail_cate_li:
                        detail_cate = li.xpath("./a/text()").extract_first()
                        detail_cate_href = li.xpath("./a/@href").extract_first()
                        print("detail_cate : ",detail_cate)
                        print("detail_cate_href : ",detail_cate_href)
                        if detail_cate:
                            item['detail_cate'] = detail_cate_href.strip()
                        if detail_cate_href:
                            item['detail_cate_href'] = detail_cate_href.strip()
                        yield scrapy.Request(item['detail_cate_href'],callback=self.parse_list,meta={"item":deepcopy(item)})

                print("-----------")

    def parse_list(self,response):
        item = deepcopy(response.meta['item'])
        if 'page_info' not in response.meta.keys():
            page_info = {}
        else:
            page_info = deepcopy(response.meta['page_info'])
        li_list = response.xpath("//div[@id='filter-results']//ul/li")
        for li in li_list:
            detail_href = li.xpath(".//div[@class='res-img']//a/@href").extract_first()
            if detail_href:
                item['detail_href'] = response.urljoin(detail_href)
            print("detail_href : ",item['detail_href'])
            title = li.xpath(".//div[@class='res-img']//a/img/@alt").extract_first()
            print("title : ",title)

            if title:
                title = title.strip()
                item['title'] = title
            else:
                item['title'] = "未知"

            yield scrapy.Request(item['detail_href'],callback=self.parse_detail,meta={"item":deepcopy(item)})

        print("翻页了---"*5)
        if 'total_page' not in page_info.keys():
            total_page = response.xpath("//span[@class='page-more']/text()").extract_first()

            print('total_page_o : ' + total_page)
            total_page = re.findall('共(\d+)页，',total_page)[0]
            print('total_page : '+total_page)
            print(type(total_page))
            page_info['total_page'] = int(total_page)
            base_url = response.xpath("//a[@class='cur']/@href").extract_first()
            print("base_url : ",base_url)
            base_url = re.findall('/1-(\d+)-(\d+)-0-0-0-0-(\d+)-0-4.html', base_url)[0][0]
            print('233 base_url : ',base_url)
            page_info['base_url'] =base_url
            print(base_url)

        if 'cur_page' not in page_info.keys():
            cur_page = 1
            page_info['cur_page'] = cur_page
        else:
            page_info['cur_page'] += 1
        if page_info['cur_page'] <page_info['total_page']:
            page_info['next_url']  = 'https://list.suning.com'+'/1-{}-{}-0-0-0-0-14-0-4.html'.format(page_info['base_url'],page_info['cur_page'])
        print('当前页 ：', page_info['cur_page'])
        print('总页数 ：', page_info['total_page'])

        # if int(cur_page)<int(total_page):
        #     next_url = '1-502324-{}-0-0-0-0-14-0-4.html'.format(str(int(cur_page)+1))

        if page_info['next_url']:
            page_info['next_url'] = response.urljoin(page_info['next_url'])
            yield scrapy.Request(url=page_info['next_url'],callback=self.parse_list,meta={"item":response.meta['item'],'page_info':page_info})


    def parse_detail(self,response):
        item = response.meta['item']
        author = response.xpath("//div[@class='proinfo-main']/ul/li[1]/text()").extract_first()
        if author:
            item['author'] = author.strip()

        else:
            item['author'] = "未知"

        publish = response.xpath("//div[@class='proinfo-main']/ul/li[2]/text()").extract_first()
        if publish:
            item['publish'] = publish.strip()
        else:
            item['publish'] = "未知"

        publish_time = response.xpath("//div[@class='proinfo-main']/ul/li[3]/text()").extract_first()
        if publish_time:
            item['publish_time'] = publish_time.strip()
        else:
            item['publish_time'] = "未知"

        print("author : ",item['author'])
        print("publish : ",item['publish'])
        print("publish_time : ",item['publish_time'])
        price_url = self.parse_price_url(response)
        if price_url:
            yield scrapy.Request(price_url,callback=self.parse_price,meta={"item":deepcopy(item)})
        else:
            item['price'] = False
            yield item


    def parse_price_url(self,response):
        text = response.text
        partNumber = re.findall('"partNumber":"(\d+)"', text)
        if not partNumber:
            return None
        else:
            partNumber = partNumber[0]
        vendorCode = re.findall('"vendorCode":"(\d+)"', text)[0]  # '"vendorCode":"0070418556"'
        catenIds = re.findall('"catenIds":"(R\d+)"', text)[0]  # '"catenIds":"R9011197"'
        brandId = re.findall('"brandId":"(\w+)"', text)[0]  # '"brandId":"0001400OD"'
        weight = re.findall('"weight":"(\d+.\d+)"', text)[0]  # '"weight":"0.6"'
        category2 = re.findall('"category2":"(\d+)"', text)[0]  # '"category2":"502320"'
        categoryId = re.findall('"categoryId":"(\d+)"', text)[0]  # '"categoryId":"502679"'

        timestamp = str(int(round(time.time() * 1000)))

        url = "https://pas.suning.com/nspcsale_0_" + partNumber + \
               "_" + partNumber + "_" + vendorCode + "_190_755_7550199_502282_1000051_9051_10346_Z001___" \
               + catenIds + "_" + weight + "____" + brandId + "____0___0.0_2__" + category2 + "_" + categoryId \
               + "_.html?callback=pcData&_=" + timestamp
        return url

    def parse_price(self,response):
        item = response.meta['item']
        text = response.text
        ret = re.findall('netPrice":"(\d+\.\d+)",', text)
        print(ret)
        if len(ret) != 0:
            print("price : "+ret[0])
            item['price'] = ret[0]
        yield item




