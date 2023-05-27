import json
import os
import subprocess
import sys

sys.path.insert(1, '/cynergy-calculator-ms/')
from ScopingCrawlerUtils.Crawlerino import crawlerino_manager
from ScopingCrawlerUtils.CustomCrawler import crawler_caller

crawling_cli_command = "'/root/go/bin/gospider' -s \'{}\' -u web -v -t 5 -c 10 -d 5 -K 5 --sitemap ""-o {}"
scrapy_crawler_command = os.path.join(os.getcwd(), 'ScopingCrawlerUtils', 'ScrapyCrawler.py')


class CrawlerManager:
    def __init__(self, target, output_folder):
        self.target = target
        self.output_folder = output_folder

    def run_crawlers(self):
        results_f_name = self.target.split("://")[1]
        results_f_name = results_f_name.replace('.', '_')
        crawler_output_dir = '{}'.format(self.output_folder)
        results_file_path = os.path.join(crawler_output_dir, results_f_name)

        # Crawler 1 - Custom Crawler
        crawler1_results = []
        try:
            crawler1_results = crawler_caller(self.target)
        except Exception as e:
            crawler1_results = []
        all_urls_crawled = crawler1_results

        # Crawler 2 - Crawlerino
        crawler2_results = []
        try:
            crawler2_results = crawlerino_manager(self.target)
        except Exception as e:
            print(e)
        all_urls_crawled = list(set(all_urls_crawled + crawler2_results))

        if os.path.exists(crawler_output_dir) and os.path.exists(results_file_path):
            os.remove(results_file_path)
        elif not os.path.exists(crawler_output_dir):
            os.mkdir(crawler_output_dir)

        # Crawler 3 - Scrapy Crawler
        subprocess.check_output(
            ' '.join(['python', scrapy_crawler_command, self.target, '{}_scrapy.json'.format(results_f_name),
                      self.output_folder]), shell=True, text=True)
        scrapy_results = []
        try:
            with open(os.path.join(self.output_folder, '{}_scrapy.json'.format(results_f_name)), 'r') as f:
                json_results = json.load(f)
                scrapy_results = [line['url'] for line in json_results]
        except:
            pass
        all_urls_crawled = list(set(all_urls_crawled + scrapy_results))

        return all_urls_crawled
