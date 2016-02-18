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
            print r


token = context.get_login_token()

# when publisher uses feedburner:
# feedburner_urls = [
#        'http://feeds.feedburner.com/TheAtlantic?format=xml'
#         ]
# for url in feedburner_urls:
#     get_rss_links(url, token, tag='feedburner_origlink')

# normal case
normal_urls = [
        'http://feeds.reuters.com/reuters/topNews?format=xml',
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://feeds.bbci.co.uk/news/rss.xml'
        ]
for url in normal_urls:
    get_rss_links(url, token)
