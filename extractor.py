import scrapy
from scrapy.crawler import CrawlerProcess
import re
import datetime

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    resultFile = "result"+datetime.datetime.now().strftime("%Y %m %d %H %M")+".csv"

    def start_requests(self):
        # urls = ["https://www.amazon.in/product-reviews/B00F178GKS/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&showViewpoints=1&pageNumber=2"]
        with open("links.txt", "r") as tp:
            urls = tp.readlines()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.rootPageParser)

    def rootPageParser(self, response):
        productUrls = response.css("a[href*=\/dp\/]::attr(href)").extract()
        reviewUrlTemplate = "https://www.amazon.in/product-reviews/@@/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&showViewpoints=1&pageNumber=2"
        for url in productUrls:
            productId = url.split("/")[3]
            productReviewUrl = reviewUrlTemplate.replace("@@",productId)
            yield scrapy.Request(url=productReviewUrl, callback=self.amazonPage)



    def amazonPage(self, response):
        #index = 3
        print(response.url)
        productId = response.url.split("/")[4]
        userIds =  response.css("a[href*=amzn1]::attr(href)").extract()[2:]
        filename = productId+".csv"
        with open(filename, "a+", encoding='utf-8') as fp:
            totalReviews = len(response.css(".a-size-base .review-text"))
            if totalReviews == 0:
                # print("no more reviews to handle")
                return
            for review in range(totalReviews):
                t = response.css(".a-size-base .review-text")[review].css("::text").extract()
                t = str(t)
                hV = response.css(".a-size-base span[data-hook*=helpful]::text").extract()[review]
                hV = re.search('^\d+',hV).group(0)
                # import pdb;pdb.set_trace()
                # print(t)
                s = response.css("i[data-hook*=review]::attr(class)")[review+2].extract()
                userName = userIds[review].split("/")[3].split(".")[-1]
                k = re.search("-([0-5])", s)[1]
                t = t.replace(","," ")
                fileLine = "\n\"%s\",\"%s\",\"%s\",\"%s\"" % (t,k,userName,hV)
                fp.write(fileLine)
                # print(k)
                pagenumber = re.search("=([0-9]+)$", response.url)[1]
                # print("page number is %s" % pagenumber)
                nextPage = int(pagenumber) + 1
                nextPageUrl = re.sub("=[0-9]+$","=" + str(nextPage), response.url)
                # print("Current page url is =%s" % response.url)
                yield scrapy.Request(url=nextPageUrl, callback=self.amazonPage)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(QuotesSpider)
process.start()
