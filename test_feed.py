import feedparser
import context
from bs4 import BeautifulSoup
import requests

# test RSS feed url
def test_rss_feed(url, token):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        print entry.id
        print entry


# working on scraping local news site without feed
# token = context.get_login_token()
# url = 'http://www.ft.com/rss/home/us'
# test_rss_feed(url, token)
url = 'http://www.gothamgazette.com/index.php/government/6234-cuomos-public-schedules-offer-little-information'
match = 'www.gothamgazette.com'
arr = []
page = requests.get(url).text
soup = BeautifulSoup(page)
for link in soup.find_all('a'):
    url = link.get('href')
    if url is not None:
        sp = url.split('/')
        if len(sp) > 1:
            if sp[2] == match:
                arr.append(url)

print arr
