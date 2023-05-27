import os
from tld import get_tld
import sys
from pathlib import Path
sys.path.insert(0, '../cynergy-calculator-ms')
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals
from ScopingCrawlerUtils.CigenCrawler.spiders.CigenCrawler import CigenCrawler
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_scrapy_crawler(target, file_name, output_path):
    target_tld_data = get_tld(target, fix_protocol=True, as_object=True)
    tld = target_tld_data.domain + '.' + target_tld_data.tld
    output_full_path = os.path.join(output_path, file_name)

    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    try:
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'DEPTH_LIMIT': 2,
            'LOG_ENABLED': True,
            'FEEDS': {
                output_full_path: {
                    'format': 'json'
                }
            },
            'REDIRECT_ENABLED': True,
            'HTTPERROR_ALLOW_ALL': True,
        })
        process.crawl(CigenCrawler, start_urls=[target], allowed_domains=[tld])
        process.start()
        if results:
            results = list(set([result['url'] for result in results]))
        return results
    except Exception as e:
        print(e)


if len(sys.argv) > 3:
    links_crawled = run_scrapy_crawler(sys.argv[1], sys.argv[2], sys.argv[3])
