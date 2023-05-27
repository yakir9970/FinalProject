import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Crawler:
    def __init__(self, urls=[]):
        self.visited_urls = []
        self.urls_to_visit = urls

    def download_url(self, url):
        return requests.get(url, verify=False).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url, target):

        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            # if tld in url:
            self.add_url_to_visit(url)

    def run(self, target):
        target_arr = target.split('://')
        tld = target_arr[1]
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            try:
                if tld in url:
                    self.crawl(url, target)
            except Exception:
                continue
            finally:
                if tld in url:
                    self.visited_urls.append(url)
                pass

        urls_data = list(dict.fromkeys(self.visited_urls))
        final_url_list = []
        for url_data in urls_data:
            if target in url_data:
                final_url_list.append(url_data)
        return final_url_list


def crawler_caller(target):
    return Crawler(urls=[target]).run(target)
