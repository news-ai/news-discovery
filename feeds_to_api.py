from __future__ import print_function
import redis
import datetime
from taskrunner import app
from celery import chain
import feedparser
from pymongo import MongoClient
import context
import json


r = redis.StrictRedis()
client = MongoClient(connect=False)
db = client.news_discovery
seen_collection = db.discovered


@app.task
def post_articles_from_redis(articles, token):
    if len(articles) > 0:
        res = context.post_article_without_author(articles, token)
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
def post_batch_articles(batch_size, _):
    feeds = json.loads(r.get('publisher_feeds'))
    for feed in feeds:
        rss_link = feed[0]
        pending_urls = json.loads(r.get(rss_link)).get('pending_urls')
        if pending_urls is not None:
            articles = []
            token = context.get_login_token()
            for article_url in pending_urls:
                print(article_url)
                if r.get(article_url):
                    article_obj = json.loads(r.get(article_url))
                    article_obj['authors'] = []
                    articles.append(article_obj)
                if len(articles) >= batch_size:
                    post_articles_from_redis(articles, token)
                    articles = []
            post_articles_from_redis(articles, token)
            remove_articles_from_redis.delay(pending_urls)
            r.set(feed[0], json.dumps({'pending_urls': []}))
    return True


# 15 min
# example: url = [RSS_LINK, ARTICLE_LINK_TAG, CAN_RUN]
@app.task
def save_all_publisher_feeds_to_redis():
    token = context.get_login_token()
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


# get_batch_articles(5)
# post_articles_from_redis(urls, token)
