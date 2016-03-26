import feedparser
import context
from bs4 import BeautifulSoup
import requests
import newspaper

# test RSS feed url
def test_rss_feed(url):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        # print entry
        print entry.id
        # print entry.feedburner_origlink
        print entry.link

def test_non_rss_page(url):
    # working on scraping local news site without feed
    # token = context.get_login_token()
    # url = 'http://www.ft.com/rss/home/us'
    # test_rss_feed(url, token)
    arr = []
    page = requests.get(url).text
    soup = BeautifulSoup(page)
    for link in soup.find_all('a'):
        url = link.get('href')
        if url is not None:
            print url
            # sp = url.split('/')
            # if len(sp) > 1:
            #     if sp[2] == match:
            #         arr.append(url)
    print arr

url_cred = 'http://www.empirestatenews.net/home/'

url1 = 'http://www.amny.com/news'
url2 = 'http://www.theepochtimes.com'
url3 = 'http://nyulocal.com'


# url = 'http://www.nydailynews.com/index_rss.xml'
# test_rss_feed(url)
# url = 'http://www.gothamgazette.com/index.php/government/6234-cuomos-public-schedules-offer-little-information'
# match = 'www.gothamgazette.com'
# url = 'http://www.dailygazette.com/news/local/'
# test_non_rss_page(url)
# url = 'http://www.qgazette.com/news.xml'
# url = 'http://www.qchron.com/search/?q=&t=article&l=100&d=&d1=&d2=&s=start_time&sd=desc&nsa=eedition&c[]=editions/south,editions/south/*&f=rss'
# test_rss_feed(url)

url = 'https://www.indypendent.org/rss.xml'
test_rss_feed(url)
