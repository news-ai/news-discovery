from __future__ import print_function
import json
import feedparser
import context
from bs4 import BeautifulSoup
import requests

# test RSS feed url


def test_rss_feed(url):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        # print entry
        print(entry.id)
        # print entry.feedburner_origlink
        print(entry.link)


def test_non_rss_page(url):
    # working on scraping local news site without feed
    # token = context.get_login_token(False)
    # url = 'http://www.ft.com/rss/home/us'
    # test_rss_feed(url, token)
    arr = []
    page = requests.get(url).text
    soup = BeautifulSoup(page)
    for link in soup.find_all('a'):
        url = link.get('href')
        if url is not None:
            print(url)
            # sp = url.split('/')
            # if len(sp) > 1:
            #     if sp[2] == match:
            #         arr.append(url)
    print(arr)

url_cred = 'http://www.empirestatenews.net/home/'

url1 = 'http://www.amny.com/news'
url2 = 'http://www.theepochtimes.com'
url3 = 'http://nyulocal.com'
url = 'https://www.indypendent.org/rss.xml'
url = 'http://espn.go.com/mlb/story/_/page/seasonpreview_wsbluejays/why-toronto-blue-jays-win-world-series'
url = 'http://www.nydailynews.com/news/crime/slain-va-trooper-made-arrest-woman-dead-son-car-article-1.2585840'
url = 'http://www.bbc.com/news/magazine-35942519'
url = 'http://www.bbc.com/news/uk-35948256'
url = 'http://www.bbc.com/news/world-europe-35948009'
url = 'http://observer.com/2016/03/rogerebert-com-holds-women-writers-week-to-celebrate-diversity/'
# test_rss_feed(url)
print(json.dumps(context.read_article_without_author(url), indent=2))
