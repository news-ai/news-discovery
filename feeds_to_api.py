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
        print res.text
        print res.status_code
        if res.status_code == 500:
            print res.text
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


@app.task
def post_batch_articles(batch_size, _):
    if r.exists('pending_urls'):
        articles = []
        token = context.get_login_token()
        article_urls = json.loads(r.get('pending_urls'))
        for article_url in article_urls:
            print article_url
            if r.get(article_url):
                article_obj = json.loads(r.get(article_url))
                article_obj['authors'] = []
                articles.append(article_obj)
            if len(articles) >= batch_size:
                post_articles_from_redis(articles, token)
                articles = []
        post_articles_from_redis(articles, token)
        remove_articles_from_redis.delay(article_urls)
        r.set('pending_urls', json.dumps([]))
    return True


# 15 min
@app.task
def save_all_publisher_feeds_to_redis():
    token = context.get_login_token()
    feed_urls = []
    res = context.get_publisher(token).json()
    for publisher in res.get('results'):
        if len(publisher.get('tags')) > 0:
            feed_urls.append([publisher['feed_url'], publisher['tags']])
        else:
            feed_urls.append([publisher['feed_url']])
    r.set('publisher_feeds', json.dumps(feed_urls))
    return True


# get_batch_articles(5)
# post_articles_from_redis(urls, token)
