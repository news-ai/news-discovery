import redis
from celery import Celery
from celery import chain
import celeryconfig
import feedparser
import context

app = Celery('feed', broker='redis://localhost:6379/0')
app.config_from_object(celeryconfig)

r = redis.StrictRedis()
# TODO: delete old articles from redis after posting


def test_rss_feed(url, token):
    d = feedparser.parse(url)
    for entry in d.get('entries'):
        print entry


# 15 min
# add batch processing
@app.task
def post_articles_from_redis(token):
    urls = r.get('pending_urls')
    for url in urls:
        article = r.get(url)
        res = context.post_article_no_author(url, article, token)
        if res.status_code == 500:
            print res.text
            print url
        return True


# FIX TO POST BY BATCH
@app.task
def post_links(rss_results, token):
    for link in rss_results:
        res = context.post_article(link, token)
        if res.status_code == 500:
            print res.text
            print link
    return True


# 15 min
@app.task
def save_all_publisher_feeds_to_redis(token):
    feed_urls = []
    res = context.get_publisher(token).json()
    for publisher in res.get('results'):
        if len(publisher.get('tags')) > 0:
            feed_urls.append([publisher['feed_url'], publisher['tags']])
        else:
            feed_urls.append([publisher['feed_url']])
    r.set('publisher_feeds', feed_urls)
    return True


if __name__ == "__main__":
    token = context.get_login_token()
    post_articles_from_redis.delay(token)
    save_all_publisher_feeds_to_redis.delay(token)
