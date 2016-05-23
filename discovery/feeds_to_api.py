# Stdlib imports
from __future__ import print_function
import datetime
import json

# Third-party app imports
import redis
import feedparser
from celery import chain
from pymongo import MongoClient

# Imports from app
from discovery.internal import context
from taskrunner import app


r = redis.StrictRedis()
client = MongoClient(connect=False)
db = client.news_discovery
seen_collection = db.discovered


@app.task
def post_articles_from_redis(articles, token):
    if len(articles) > 0:
        res = context.post_article_without_author(articles, token, False)
        print(res.text)
        print(res.status_code)
        if res.status_code == 500:
            print(res.text)
    return True


@app.task
def remove_articles_from_redis(article_urls):
    for url in article_urls:
        r.delete(url)
        post = {
            'url': url,
            'date': datetime.datetime.utcnow()
        }
        seen_collection.insert_one(post)
    return True

# in REDIS
# feed_link : { pending_urls: [url1, url2, url3] }


@app.task
def post_batch_articles(batch_size, rss_link, token):
    pending_obj = r.get(rss_link)
    if pending_obj is None:
        r.set(rss_link, json.dumps({'pending_urls': []}))
        return False
    pending_urls = json.loads(pending_obj).get('pending_urls')
    if len(pending_urls) > 0:
        articles = []
        for article_url in pending_urls:
            print(article_url)
            if r.get(article_url):
                article_obj = json.loads(r.get(article_url))
                article_obj['authors'] = []
                articles.append(article_obj)
            if len(articles) >= batch_size:
                post_articles_from_redis(articles, token)
                articles = []
        print(articles)
        post_articles_from_redis.delay(articles, token)
        remove_articles_from_redis.delay(pending_urls)
        r.set(rss_link, json.dumps({'pending_urls': []}))
    return True


@app.task
def post_articles_for_each_feed():
    feeds = json.loads(r.get('publisher_feeds'))
    token = context.get_login_token(False)
    for feed in feeds:
        rss_link = feed[0]
        post_batch_articles.delay(10, rss_link, token)
    return True


# 15 min
# example: url = [RSS_LINK, ARTICLE_LINK_TAG, CAN_RUN]
@app.task
def save_all_publisher_feeds_to_redis():
    token = context.get_login_token(False)
    feed_urls = []
    res = context.get_publisher(token).json()
    for publisher in res.get('results'):
        if len(publisher.get('tags')) > 0:
            feed_urls.append([publisher['feed_url'], publisher['tags'], True])
        else:
            feed_urls.append([publisher['feed_url'], None, True])

    # add all non-feed url
    feed_urls.append(['http://www.nytimes.com', None, False])

    r.set('publisher_feeds', json.dumps(feed_urls))
    return True


# save_all_publisher_feeds_to_redis.delay()
# post_articles_for_each_feed.delay()
