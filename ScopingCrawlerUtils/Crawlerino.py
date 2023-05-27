import bs4
import requests
import collections
import string
from urllib.parse import urldefrag, urljoin, urlparse
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# GLOBALS
return_data = []


def crawler(startpage, maxpages=1000, singledomain=True):
    global return_data
    pagequeue = collections.deque()  # queue of pages to be crawled
    pagequeue.append(startpage)
    crawled = []  # list of pages already crawled
    domain = urlparse(startpage).netloc if singledomain else None

    pages = 0  # number of pages succesfully crawled so far
    failed = 0  # number of links that couldn't be crawled

    sess = requests.session()
    while pages < maxpages and pagequeue:
        url = pagequeue.popleft()
        # read the page
        try:
            response = sess.get(url, verify=False)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
            print("*FAILED*:", url)
            failed += 1
            continue
        if not response.headers["content-type"].startswith("text/html"):
            continue  # don't crawl non-HTML content

        # Note that we create the Beautiful Soup object here (once) and pass it
        # to the other functions that need to use it
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # process the page
        crawled.append(url)
        return_data.append(url)
        pages += 1
        if pagehandler(url, response, soup):
            # print(' ---> {}'.format(url))
            # get the links from this page and add them to the crawler queue
            links = getlinks(url, domain, soup)
            for link in links:
                if not url_in_list(link, crawled) and not url_in_list(link, pagequeue):
                    pagequeue.append(link)
                    return_data.append(link)


def getcounts(words=None):
    # create a dictionary of key=word, value=count
    counts = collections.Counter(words)
    # save total word count before removing common words
    wordsused = len(counts)
    # remove common words from the dictionary
    shortwords = [word for word in counts if len(word) < 3]  # no words <3 chars
    ignore = shortwords + [
        "after",
        "all",
        "and",
        "are",
        "because",
        "been",
        "but",
        "for",
        "from",
        "has",
        "have",
        "her",
        "more",
        "not",
        "now",
        "our",
        "than",
        "that",
        "the",
        "these",
        "they",
        "their",
        "this",
        "was",
        "were",
        "when",
        "who",
        "will",
        "with",
        "year",
        "hpv19slimfeature",
        "div",
    ]
    for word in ignore:
        counts.pop(word, None)

    # remove words that contain no alpha letters
    tempcopy = [_ for _ in words]
    for word in tempcopy:
        if noalpha(word):
            counts.pop(word, None)
    return (counts, wordsused)


def getlinks(pageurl, domain, soup):
    # get target URLs for all links on the page
    links = [a.attrs.get("href") for a in soup.select("a[href]")]
    # remove fragment identifiers
    links = [urldefrag(link)[0] for link in links]
    # remove any empty strings
    links = [link for link in links if link]
    # if it's a relative link, change to absolute
    links = [
        link if bool(urlparse(link).netloc) else urljoin(pageurl, link)
        for link in links
    ]
    # if only crawing a single domain, remove links to other domains
    if domain:
        links = [link for link in links if samedomain(urlparse(link).netloc, domain)]
    return links


def getwords(rawtext):
    words = []
    cruft = ',./():;!"' + "<>'â{}"  # characters to strip off ends of words
    for raw_word in rawtext.split():
        # remove whitespace before/after the word
        word = raw_word.strip(string.whitespace + cruft + "-").lower()
        # remove posessive's at end of word
        if word[-2:] == "'s":
            word = word[:-2]
        if word:  # if there's anything left, add it to the words list
            words.append(word)
    return words


def pagehandler(pageurl, pageresponse, soup):
    # print("Crawling:" + pageurl + " ({0} bytes)".format(len(pageresponse.text)))
    # wordcount(soup) # display unique word counts
    return True


def noalpha(word):
    for char in word:
        if char.isalpha():
            return False
    return True


def samedomain(netloc1, netloc2):
    domain1 = netloc1.lower()
    if "." in domain1:
        domain1 = domain1.split(".")[-2] + "." + domain1.split(".")[-1]
    domain2 = netloc2.lower()
    if "." in domain2:
        domain2 = domain2.split(".")[-2] + "." + domain2.split(".")[-1]
    return domain1 == domain2


def url_in_list(url, listobj):
    http_version = url.replace("https://", "http://")
    https_version = url.replace("http://", "https://")
    return (http_version in listobj) or (https_version in listobj)


def wordcount(soup):
    rawtext = soup.get_text()
    words = getwords(rawtext)
    counts, _ = getcounts(words)
    if counts.most_common(1)[0][1] < 10:
        print("This page does not have any words used more than 10 times.")
    else:
        print(counts.most_common(10))


# if running standalone, crawl some Microsoft pages as a test
def crawlerino_manager(target):
    global return_data
    crawler(target, maxpages=10)
    return list(dict.fromkeys(return_data))


