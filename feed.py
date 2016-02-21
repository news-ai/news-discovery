import feedparser
import context


def get_rss_links(url, token, tag='id'):
    ret = []
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        print entry.get(tag)
        ret.append(entry.get(tag))

    if len(ret) > 0:
        for link in ret:
            r = context.post_article(link, token)
            if r.status_code == 500:
                print r.text
                print link

def test_rss_feed(url, token):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        print entry

def post_all_feeds():
    token = context.get_login_token()

    # # when publisher rss feed has custom tags:
    custom_urls = [
           ['http://feeds.feedburner.com/TheAtlantic?format=xml', 'feedburner_origlink'],
           ['http://feeds.foxnews.com/foxnews/latest', 'link'],
           ['http://espn.go.com/espn/rss/news', 'link'],
           ['http://espn.go.com/espn/rss/nfl/news', 'link'],
           ['http://espn.go.com/espn/rss/nba/news', 'link'],
           ['http://espn.go.com/espn/rss/mlb/news', 'link'],
           ['http://espn.go.com/espn/rss/nhl/news', 'link'],
           ['http://espn.go.com/espn/rss/rpm/news', 'link'],
           ['http://espn.go.com/espn/rss/espnu/news', 'link'],
           ['http://espn.go.com/espn/rss/ncb/news', 'link'],
           ['http://espn.go.com/espn/rss/ncf/news', 'link'],
           ['http://espn.go.com/espn/rss/action/news', 'link'],
           ['http://espn.go.com/espn/rss/poker/news', 'link'],
           ['http://www.espnfc.com/rss', 'link']
           ]
    for i in xrange(0, len(custom_urls)):
        get_rss_links(custom_urls[i][0], token, tag=custom_urls[i][1])

    # # # normal case
    normal_urls = [
            'http://feeds.reuters.com/reuters/topNews?format=xml',
            'http://rss.cnn.com/rss/cnn_topstories.rss',
            'http://feeds.bbci.co.uk/news/rss.xml'
            ]
    for url in normal_urls:
        get_rss_links(url, token)


# url = 'http://espn.go.com/espn/rss/nfl/news'
# url = 'http://www.espnfc.com/rss'
# get_rss_links(url, token)
