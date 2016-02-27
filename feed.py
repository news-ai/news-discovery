from celery import Celery
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
def get_rss_results(url, tag='id'):
    ret = []
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        ret.append(entry.get(tag))
    return ret


@app.task
def post_links(rss_results, token):
    for link in rss_results:
        r = context.post_article(link, token)
        print 'yee'
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
    urls = get_all_feeds.AsyncResult(token)

    if urls.ready():
        for url in urls:
            if len(url) > 1:
                rss = get_rss_results.AsyncResult(url, tag=url[1])
            else:
                rss = get_rss_results.AsyncResult(url)

            if rss.ready():
                post_links(rss, token)
    return True


if __name__ == "__main__":
    post_all_feeds.delay()
