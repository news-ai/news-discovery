import feedparser
import context

def get_bbc_world_links(token):
    ret = []
    d = feedparser.parse('http://feeds.bbci.co.uk/news/world/rss.xml')
    for entry in d['entries']:
        ret.append(entry['id'])

    if len(ret) > 0:
        for link in ret:
            r = context.post_article(link, token)
            print r

token = context.get_login_token()
get_bbc_world_links(token)
