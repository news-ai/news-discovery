import feedparser
import context


def get_bbc_world_links(url, token):
    ret = []
    d = feedparser.parse(url)
    for entry in d['entries']:
        ret.append(entry['id'])

    if len(ret) > 0:
        for link in ret:
            r = context.post_article(link, token)
            print r

token = context.get_login_token()
url = 'http://feeds.bbci.co.uk/news/rss.xml'
get_bbc_world_links(url, token)
