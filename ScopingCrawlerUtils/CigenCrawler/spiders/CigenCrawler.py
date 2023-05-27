import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from tld import get_tld
from ScopingCrawlerUtils.CigenCrawler.items import CigenItem
import sys
sys.path.insert(0, '../cynergy-calculator-ms')

JS_SNIPPET = 'window.scrollTo(0, document.body.scrollHeight);'


class CigenCrawler(CrawlSpider):
    name = "cigencrawler"
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True,
                tags=('a', 'form', 'input'),
                attrs=('href', 'action', 'src'),
            ),
            follow=True,
            callback='parse_items'
        ),
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True)
            yield scrapy.Request('{}/sign-in'.format(url), callback=self.parse_items)
            yield scrapy.Request('{}/log-in'.format(url), callback=self.parse_items)
            yield scrapy.Request('{}/sign-up'.format(url), callback=self.parse_items)
            yield scrapy.Request('{}/register'.format(url), callback=self.parse_items)

    def parse_items(self, response):
        items = []
        print(response.status)
        links = self.rules[0].link_extractor.extract_links(response)
        for link in links:
            target_tld_data = get_tld(link.url, fix_protocol=True, as_object=True)
            tld = target_tld_data.domain + '.' + target_tld_data.tld
            if self.allowed_domains[0] in tld:
                item = CigenItem()
                item['url'] = link.url
                items.append(item)
                yield item
                yield scrapy.Request(link.url, dont_filter=True)
