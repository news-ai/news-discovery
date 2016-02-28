import redis
from celery import Celery
from celery import chain
import celeryconfig
import feedparser
import context
import json

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
def post_articles_from_redis(articles, token):
    res = context.post_article_without_author(articles, token)
    print res.text
    if res.status_code == 500:
        print res.text
    return True


@app.task
def get_batch_articles():
    articles = []
    article_urls = json.loads(r.get('pending_urls'))
    for article_url in article_urls:
        article_obj = json.loads(r.get(article_url))
        articles.append(article_obj)
    return articles


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
    r.set('publisher_feeds', json.dumps(feed_urls))
    return True


@app.task
def post_all_feeds(token):
    chain = get_batch_articles.s() | post_articles_from_redis.s(token)
    chain()
    return True


if __name__ == "__main__":
    token = context.get_login_token()
    post_all_feeds.delay(token)
    save_all_publisher_feeds_to_redis.delay(token)
    # token = context.get_login_token()
    # save_all_publisher_feeds_to_redis(token)
    # print r.get('publisher_feeds')
