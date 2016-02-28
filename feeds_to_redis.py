import redis
from taskrunner import app
from celery import chain
import celeryconfig
import requests
import feedparser
import context
import os
import json

r = redis.StrictRedis()
# TODO: delete old articles from redis after posting


@app.task
def get_all_publisher_feeds_from_redis():
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
    if r.exists('pending_urls') == False:
        r.set('pending_urls', json.dumps([]))
    article_links = []
    for url in urls:
        if r.exists(json.dumps(url)) == False:
            urls = json.loads(r.get('pending_urls'))
            urls.append(url)
            r.set('pending_urls', json.dumps(urls))
            article_links.append(url)
    return article_links


@app.task
def save_articles_to_redis(urls):
    for url in urls:
        article = json.dumps(context.read_article_without_author(url))
        r.set(url, article)
    return True


@app.task
def get_nytimes_links():
    newswire = 'http://api.nytimes.com/svc/news/v3/content/all/all.json?api-key=' + \
        os.environ.get('NYTIMES')
    data = requests.get(newswire).json()
    urls = []
    for result in data['results']:
        url = result.get('url')
        if url is not None:
            urls.append(url)
    return urls


@app.task
def run_nytimes():
    chain = get_nytimes_links.s() | save_article_links_to_redis.s() | \
            save_articles_to_redis.s()
    chain()
    return True


@app.task
def save_all_feeds_to_redis():
    chain = get_all_publisher_feeds_from_redis.s() | \
        get_rss_from_publisher_feeds.s() | \
        save_article_links_to_redis.s() | \
        save_articles_to_redis.s()
    chain()
    return True
