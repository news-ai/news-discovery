from celery import Celery
from celery import chain
import celeryconfig
import feedparser
import context

app = Celery('feed', broker='redis://localhost:6379/0')
app.config_from_object(celeryconfig)


def test_rss_feed(url, token):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        print entry


@app.task
def get_rss_results(urls):
    ret = []
    for url in urls:
        d = feedparser.parse(url[0])
        for entry in d.get('entries'):
            if len(url) == 1:
                ret.append(entry.get('id'))
            else:
                ret.append(entry.get(url[1]))
    return ret


@app.task
def post_links(rss_results, token):
    for link in rss_results:
        r = context.post_article(link, token)
        if r.status_code == 500:
            print r.text
            print link
    return True


@app.task
def get_all_feeds(token):
    feed_urls = []
    r = context.get_publisher(token).json()
    for publisher in r.get('results'):
        if len(publisher.get('tags')) > 0:
            feed_urls.append([publisher['feed_url'], publisher['tags']])
        else:
            feed_urls.append([publisher['feed_url']])
    return feed_urls


@app.task
def post_all_feeds():
    token = context.get_login_token()
    # urls = get_all_feeds.delay(token)
    chain = get_all_feeds.s(token) | get_rss_results.s() | post_links.s(token)
    chain()
    return True


if __name__ == "__main__":
    post_all_feeds.delay()
