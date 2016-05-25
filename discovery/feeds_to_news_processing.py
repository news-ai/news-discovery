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

# Setting up Redis & Mongo Instances
r = redis.StrictRedis()
client = MongoClient(connect=False)
db = client.news_discovery
seen_collection = db.discovered


# in REDIS
# feed_link : { pending_urls: [url1, url2, url3] }

@app.task
def remove_articles_from_redis(article_urls):
    for article_url in article_urls:
        r.delete(article_url)
        post = {
            'url': article_url,
            'date': datetime.datetime.utcnow()
        }
        seen_collection.insert_one(post)
    return True


@app.task
def post_articles_from_redis(article_urls):
    if len(article_urls) > 0:
        res = None
        for article_url in article_urls:
            res = context.post_to_news_processing(article_url)
            if res.status_code == 500:
                print(res.text)
    return True


@app.task
def post_batch_articles(rss_link):
    pending_obj = r.get(rss_link)
    if pending_obj is None:
        r.set(rss_link, json.dumps({'pending_urls': []}))
        return False
    pending_urls = json.loads(pending_obj).get('pending_urls')
    if len(pending_urls) > 0:
        post_articles_from_redis.delay(pending_urls)
        remove_articles_from_redis.delay(pending_urls)
        r.set(rss_link, json.dumps({'pending_urls': []}))
    return True


@app.task
def post_articles_for_each_feed():
    feeds = json.loads(r.get('publisher_feeds'))
    for feed in feeds:
        rss_link = feed[0]
        post_batch_articles.delay(rss_link)
    return True
