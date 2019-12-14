import scrapy
import sys
import sqlite3
from scrapy.crawler import CrawlerProcess
from multiprocessing import pool

# from .models import product
# import scrapy_proxy_pool

class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product = scrapy.Field()
    next_pg = scrapy.Field()
    pass

def crawl(query):
    items = []
    process = CrawlerProcess({
        'ROBOTSTXT_OBEY' : 'False',
        'COOKIES_ENABLED' : 'False',
        # 'PROXY_POOL_ENABLED' : 'True',
        # 'DOWNLOAD_DELAY' : '0.25',
        # 'DOWNLOADER_MIDDLEWARES' : {
        #      'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        #      'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        #      'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
        #      'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
        # }   
    })

    amazon = 'https://www.amazon.com/' + query + '/s?k='
    alibaba = 'https://www.alibaba.com/catalogs/search?&SearchText='
    ebay =  'https://www.ebay.com/sch/i.html?_nkw='

    amazonq = amazon + query #+ '&page=2'
    alibabaq = alibaba + query #+ '&page=2' 
    ebayq = ebay + query #+ '&_pgn=2'

    process.crawl(AmspSpider, query = amazonq)
    process.crawl(AlispSpider, query = alibabaq)
    process.crawl(EbaySpider, query = ebayq)
    process.start()
    items.append(AmspSpider.items)
    items.append(EbaySpider.items)
    items.append(AlispSpider.items)
    return items

class AlispSpider(scrapy.Spider):
    name = 'alisp'
    allowed_domains = ['alibaba.com']
    start_urls = []
    items = Items()

    def __init__(self, query = None):
        self.start_urls = [query]

    def parse(self, response):
        item_x = response.css('.m-gallery-product-item-v2')
        
        if len(item_x) == 0:
            item_x = response.css('.s-include-content-margin')
        
        itemlst = []
        
        for i in range(0, len(item_x)):
            product = dict.fromkeys(['title', 'price', 'imglnk', 'link'])
            # title = item_x[i].css('.title a').css('::attr(title)').extract_first()
            title = item_x[i].css('.offer-image-box img').css('::attr(alt)').extract_first()
            price = item_x[i].css('.price b').css('::text').extract_first()
            imglnk = item_x[i].css('.offer-image-box img').css('::attr(data-src)').extract_first()  
            if imglnk == None:
                imglnk = item_x[i].css('.offer-image-box img').css('::attr(src)').extract_first()
            link = item_x[i].css('.title a').css('::attr(href)').extract_first()    
            product['title'] = title
            product['price'] = str(price).strip()
            product['imglnk'] = imglnk
            product['link'] = link
            if ((product['title'] is not None) 
                and (product['price'] is not None)
                and (product['imglnk'] is not None)
                and (product['link'] is not None)):
                itemlst.append(product)

        next_pg = response.url +  '&page=2'
        self.items['next_pg'] = next_pg
        self.items['product'] = itemlst
        # yield self.items['product']
        pass

class AmspSpider(scrapy.Spider):
    name = 'amsp'
    allowed_domains = ['amazon.com']
    start_urls = []
    items = Items()
    count = 0
    def __init__(self, query = None):
        self.start_urls = [query]


    def parse(self, response):
        
        item_x = response.css('.sg-col-24-of-28~ .sg-col-24-of-28+ .sg-col-24-of-28 .s-border-bottom')
        
        if len(item_x) == 0:
            item_x = response.css('.s-include-content-margin')
        itemlist = []
        
        for each in item_x:
            product = dict.fromkeys(['title', 'price', 'imglnk', 'link'])
            title = each.css('.a-color-base.a-text-normal').css('::text').extract_first()
            price = each.css('.a-offscreen::text').extract_first()
            if price == None:
                price = each.css('.a-color-secondary .a-color-base').css('::text').extract_first()
            imglnk = each.css('.s-image::attr(src)').extract_first()
            link = each.css('.a-link-normal::attr(href)').extract_first()
            link = response.urljoin(link)    
            product['title'] = title
            product['price'] = price
            product['imglnk'] = imglnk
            product['link'] = link
            if ((product['title'] is not None) 
                and (product['price'] is not None)
                and (product['imglnk'] is not None)
                and (product['link'] is not None)):
                itemlist.append(product)
            
        next_pg = response.css('.a-last a::attr(href)').extract_first()
        next_pg = response.urljoin(next_pg)
        self.items['next_pg'] = next_pg
        self.items['product'] = itemlist
        # yield self.items['product']
        pass

class EbaySpider(scrapy.Spider):
    name = 'ebaysp'
    # allowed_domains = ['ebay.com']
    start_urls = ['https://www.ebay.com/sch/i.html?_nkw=']
    items = Items()


    def __init__(self, query = None):
        self.start_urls = [query]


    def parse(self, response):

        item_x = response.css('.s-item__wrapper')
        itemlist = []
        
        for each in item_x:
            product = dict.fromkeys(['title', 'price', 'imglnk', 'link'])
            title = each.css('.s-item__title').extract_first()
            title = title.replace('<span class="LIGHT_HIGHLIGHT">New Listing</span>', '')
            title = title.replace('<h3 class="s-item__title">', '')
            title = title.replace('</h3>', '')
            price = each.css('.s-item__price').extract_first().replace('<span class="DEFAULT">', "")
            price = price.replace('</span>', " ")
            price = price.replace('<span class="s-item__price">', "")
            imglnk = each.css('.s-item__image-img').css('::attr(data-src)').extract_first()
            if imglnk is None:
                imglnk = each.css('.s-item__image-img').css('::attr(src)').extract_first()
            link = each.css('.s-item__link').css('::attr(href)').extract_first()
            product['title'] = title
            product['price'] = price
            product['imglnk'] = imglnk
            product['link'] = link
            if ((product['title'] is not None) 
                and (product['price'] is not None)
                and (product['imglnk'] is not None)
                and (product['link'] is not None)):
                itemlist.append(product)

        next_pg = response.css('.x-pagination__ol+ .x-pagination__control').css('::attr(href)').extract_first()
        next_pg = response.urljoin(next_pg)
        self.items['next_pg'] = next_pg
        self.items['product'] = itemlist
        # yield self.items['product']
        pass     

if __name__ == "__main__":
    query = sys.argv[1]
    for i in range(2, len(sys.argv)):
        query = query + '+' + sys.argv[i]
    data = crawl(query)
    for l in range(len(data)):
        for j in data[l]['product']:
            j['title'] = "".join(i for i  in j['title'] if ord(i)<128) #removing non-Acsii
            print(j['title'] + "**")
            print(j['link'] + "**") 
            print(j['imglnk'] + "**")
            print(j['price'] + "**")

