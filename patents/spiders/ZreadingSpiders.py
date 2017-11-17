# -*- coding: utf-8 -*-
import scrapy
from patents.items import ZreadingItem
from scrapy.http import Request
import re
from scrapy.selector import Selector
class ZreadingSpiders(scrapy.Spider):
    name = "zreading"  # the name of spider
    allowed_domain = ['zreading.cn']  # allowed domain for spiders
    start_urls = [
         'http://www.zreading.cn'  # the start url / the entrance of spider
    ]
    def parse(self, response):
        if response.url.endswith('html'):
            item = self.parsePaperContent(response)
        else:
            # get all the page links in list Page
            sel = Selector(response)
            links = sel.xpath('//*[@id="content"]/article/header/h2/a/@href').extract()
            for link in links:
                yield Request(link, callback=self.parse)

            # get the next page to visitr
            next_pages = sel.xpath('//*[@id="content"]/div/a[@class="next"]/@href').extract()
            if len(next_pages) != 0:
                yield Request(next_pages[0], callback=self.parse)
                # record the list page

        yield item

    def parsePaperContent(self, response):
        print "In parsse paper content function......"
        # get the page number  '5412.html'
        #  page_id = response.url.split('/')[-1].split('.')[0] ----- OK
        r = re.match(r'\d+', response.url.split('/')[-1])
        page_id = r.group()
        # instantie the item
        zding = ZreadingItem()
        sel = Selector(response)
        # add tilte
        title = sel.xpath("//div[@id='content']/article/header/h2/text()").extract()[0]
        s_title = title.encode("utf-8")
        zding['title'] = s_title.lstrip().rstrip()

        # add pub_date
        pub_date = sel.xpath('//*[@id="' + page_id + '"]/div[2]/span[1]/text()').extract()[0]
        s_pub_date = pub_date.encode("utf8")
        zding['pub_date'] = s_pub_date.lstrip().rstrip()

        # add author
        author = sel.xpath('//*[@id="' + page_id + '"]/div[2]/span[2]/a/text()').extract()[0]
        s_author = author.encode("utf8")
        zding['author'] = s_author.lstrip().rstrip()

        # add tags including type and paper tags

        tags = sel.xpath('//*[@id="' + page_id + '"]/div[2]/a/text()').extract()
        tags = [s.encode('utf8') for s in tags]
        zding['types'] = tags[0]
        zding['tags'] = "+".join(tags[1:])

        # add view count
        views = sel.xpath('//*[@id="' + page_id + '"]/div[2]/span[3]/text()').extract()[0]
        r = re.search(r'\d+', views)
        view_count = int(r.group())
        zding['view_count'] = view_count
        # add content
        content = sel.xpath('//*[@id="' + page_id + '"]/div[3]/p/text()').extract()
        zding['content'] = "\n".join(content)

        # return the item
        return zding