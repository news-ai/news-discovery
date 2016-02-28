import redis
from celery import Celery
from celery import chain
import celeryconfig
import feedparser
import context
import json

app = Celery('feeds_to_redis', broker='redis://localhost:6379/0')
app.config_from_object(celeryconfig)

r = redis.StrictRedis()
# TODO: delete old articles from redis after posting


@app.task
def get_all_redis_publisher_feeds():
    return json.loads(r.get('publisher_feeds'))


@app.task
def get_rss_from_publisher_feeds(feeds):
    article_links = []
    for url in feeds:
        d = feedparser.parse(url[0])
        # print d
        for entry in d.get('entries'):
            if len(url) == 1:
                article_links.append(entry.get('id'))
            else:
                article_links.append(entry.get(url[1]))
    return article_links


@app.task
def save_article_links_to_redis(urls):
    r.set('pending_urls', json.dumps(urls))
    return urls


@app.task
def save_articles_to_redis(urls):
    for url in urls:
        article = json.dumps(context.read_article_without_author(url))
        r.set(url, article)
    return True


@app.task
def save_all_feeds_to_redis():
    chain = get_all_redis_publisher_feeds.s() | \
        get_rss_from_publisher_feeds.s() | \
        save_article_links_to_redis.s() | \
        save_articles_to_redis.s()
    chain()
    print r.get('pending_urls')
    return True


if __name__ == "__main__":
    save_all_feeds_to_redis.delay()
