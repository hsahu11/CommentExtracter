import scrapy
from scrapy.crawler import CrawlerProcess
import re
import datetime

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    resultFile = "result"+datetime.datetime.now().strftime("%Y %m %d %H %M")+".csv"

    def start_requests(self):
        urls = [
       "https://www.amazon.in/product-reviews/B00F178GKS/ref=acr_offerlistingpage_text?ie=UTF8&showViewpoints=1"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.amazonPage)

    def amazonPage(self, response):
        index = 3
        t = response.css(".a-size-base .review-text")[index].css("::text").extract()
        print(t)
        s = response.css("i[data-hook*=review]::attr(class)")[index+2].extract()
        k = re.search("-([0-5])", s)[1]
        print(k)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(QuotesSpider)
process.start()
