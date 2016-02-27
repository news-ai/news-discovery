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


# 1 min
@app.task
def get_all_redis_publisher_feeds():
    return r.get('publisher_feeds')


# 1 min
@app.task
def get_rss_from_publisher_feeds(urls):
    article_links = []
    for url in urls:
        d = feedparser.parse(url[0])
        for entry in d.get('entries'):
            if len(url) == 1:
                ret.append(entry.get('id'))
            else:
                ret.append(entry.get(url[1]))
    return article_links


# 1 min
@app.task
def save_article_links_to_redis(urls):
    r.set('pending_urls', urls)
    return True


# 1 min
@app.task
def save_articles_to_redis(urls):
    for url in urls:
        article = context.read_article_without_author(url)
        r.set(url, article)
    return True


# 1 min
@app.task
def save_all_feeds_to_redis():
    chain = get_all_redis_publisher_feeds.s() | \
        get_rss_from_publisher_feeds.s() | \
        save_article_links_to_redis.s() | \
        save_articles_to_redis.s()
    chain()
    return True


if __name__ == "__main__":
    publisher_feeds = get_all_redis_publisher_feeds()
    article_links = get_rss_from_publisher_feeds(publisher_feeds)
    save_articles_to_redis(article_links)
    save_articles_to_redis(article_links)
    print 'Done'
    print

