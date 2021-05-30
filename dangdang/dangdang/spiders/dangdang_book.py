import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy


class DangdangBookSpider(scrapy.Spider):
    name = 'dangdang_book'
    # redis_key = 'dangdang:start_urls'
    start_urls = ['http://book.dangdang.com/']
    allowed_domains = ['dangdang.com']

    def parse(self, response):
        item = {}
        with open("dang.html","w") as f:
            f.write(response.text)
        div_list = response.xpath("//div[@class='con flq_body']/div")
        for div in div_list[:-4]:
            big_cate = div.xpath("./dl/dt//text()").extract()
            big_cate = [i.strip() for i in big_cate if len(i.strip())>0]
            big_cate = "".join(big_cate)
            print(big_cate)
            item['big_cate'] = big_cate
            dl_list = div.xpath(".//dl[@class='inner_dl']")
            for dl in dl_list:
                mid_cate = dl.xpath("./dt//text()").extract_first()
                if not mid_cate.strip():
                    mid_cate = dl.xpath("./dt//text()").extract()[1]
                    print(mid_cate)
                    item['mid_cate'] = mid_cate.strip()
                else:
                    print(mid_cate.strip())
                    item['mid_cate'] = mid_cate.strip()
                a_list = dl.xpath("./dd/a")
                for a in a_list:
                    small_cate = a.xpath("./@title").extract_first()
                    small_cate_url = a.xpath("./@href").extract_first()
                    item['small_cate'] = small_cate
                    item['small_cate_url'] = small_cate_url
                    print(small_cate)
                    print(small_cate_url)
                    yield scrapy.Request(url=small_cate_url,callback=self.parse_list,meta={"item":deepcopy(item)})
                    break
                break
            break

            print("*"*30)

    def parse_list(self,response):
        item = response.meta['item']
        if "html" in response.request.url:
            detail_li = response.xpath("//ul[@class='bigimg']/li")
            for li in detail_li:
                detail_url = li.xpath("./a/@href").extract_first()
                print(detail_url)
                item['detail_url'] = detail_url
                yield scrapy.Request(url=detail_url,callback=self.parse_detail,meta={"item":deepcopy(item)})
        else:
            map_list = response.xpath('//*[@id="bd"]/div/div[2]/map')
            for map in map_list:
                detail_urls = map.xpath("./area/@href").extract()
                if len(detail_urls)>1:
                    for detail_url in detail_urls:
                        print("233",detail_url)
                        item['detail_url'] = detail_url
                        yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": deepcopy(item)})
                else:
                    print("233",detail_urls[0])
                    item['detail_url'] = detail_urls[0]
                    yield scrapy.Request(url=detail_urls[0], callback=self.parse_detail, meta={"item": deepcopy(item)})
            li_list = response.xpath("//ul[@class='list_aa ']/li")
            for li in li_list:
                detail_url = li.xpath("./a/@href").extract_first()
                print(detail_url)
                item['detail_url'] = detail_url
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"item": deepcopy(item)})

    def parse_detail(self,response):
        item= response.meta['item']
        title = response.xpath('//*[@id="product_info"]/div[1]/h1/@title').extract_first()
        head_name = response.xpath('//*[@id="product_info"]/div[1]/h2/span/@title').extract()
        head_name = "".join(head_name)
        try:
            original_price = response.xpath('//*[@id="original-price"]/text()').extract()[1].strip()
        except:
            original_price = None
        cur_price = response.xpath('//*[@id="dd-price"]/text()').extract()
        item['title'] = title
        item['head_name'] = head_name
        item['original_price'] = original_price
        item['cur_price'] = cur_price
        print(item)
        yield item




