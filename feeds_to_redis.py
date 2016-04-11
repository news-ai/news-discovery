from __future__ import print_function
import redis
from pymongo import MongoClient
from taskrunner import app
from celery import chain
import requests
import feedparser
import context
import os
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# Removing requests warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

r = redis.StrictRedis()
client = MongoClient(connect=False)
db = client.news_discovery
seen_collection = db.discovered


@app.task
def check_publisher_feeds():
    # updates the list of publisher feeds that we are checking
    if r.exists('publisher_feeds') is False:
        token = context.get_login_token()
        feed_urls = []
        res = context.get_publisher(token).json()
        for publisher in res.get('results'):
            if len(publisher.get('tags')) > 0:
                feed_urls.append([
                    publisher['feed_url'],
                    publisher['tags'],
                    True
                    ])
            else:
                feed_urls.append([publisher['feed_url'], None, True])
        feed_urls.append(['http://www.nytimes.com', None, False])
        r.set('publisher_feeds', json.dumps(feed_urls))
    return True


@app.task
def get_rss_from_publisher_feeds(feed):
    article_links = []
    # e.g. url = [RSS_LINK, ARTICLE_LINK_TAG, CAN_RUN]
    rss_link = feed[0]
    rss_tag = feed[1]
    can_run = feed[2]
    if can_run:
        d = feedparser.parse(rss_link)
        for entry in d.get('entries'):
            if rss_tag is None:
                rss_tag = 'id'
            if entry.get(rss_tag):
                article_links.append(entry.get(rss_tag))
    save_article_links_to_redis.delay(article_links, rss_link)
    return True


@app.task
def save_article_links_to_redis(urls, rss_link):
    pending_obj = r.get(rss_link)
    if pending_obj is None:
        pending_urls = []
    else:
        pending_obj = json.loads(pending_obj)
        pending_urls = pending_obj.get('pending_urls', [])
    article_links = []
    for url in urls:
        if seen_collection.find_one({'url': url}) is None:
            pending_urls.append(url)
            obj = {'pending_urls': pending_urls}
            r.set(rss_link, json.dumps(obj))
            article_links.append(url)
    print(article_links)
    save_articles_to_redis.delay(article_links)
    return True


@app.task
def save_articles_to_redis(urls):
    for url in urls:
        try:
            article = json.dumps(context.read_article_without_author(url))
            r.set(url, article)
            r.expire(url, 60 * 30)
        except Exception as e:
            print(e)
            pass
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

    NY_TIMES_FEED = 'http://www.nytimes.com'
    pending_obj = r.get(NY_TIMES_FEED)
    if pending_obj is None:
        pending_urls = []
    else:
        pending_urls = json.loads(r.get(NY_TIMES_FEED)).get('pending_urls')
    if pending_urls is None:
        r.set(NY_TIMES_FEED, json.dumps({'pending_urls': []}))
        pending_urls = []
    for url in urls:
        if seen_collection.find_one({'url': url}) is None:
            pending_urls.append(url)
    r.set(NY_TIMES_FEED, json.dumps({'pending_urls': pending_urls}))
    return True


# add expiry time to 10 min to prevent task queue blow up
@app.task
def save_all_articles_to_redis():
    check_publisher_feeds()
    feeds = r.get('publisher_feeds')
    if feeds is None:
        return False
    feeds = json.loads(feeds)
    for feed in feeds:
        print(feed)
        get_rss_from_publisher_feeds.delay(feed)
    return True

# save_all_articles_to_redis.delay()

# check_publisher_feeds()
# pub_links = get_all_publisher_feeds_from_redis()
# article_links = get_rss_from_publisher_feeds(pub_links)
# article_links = save_article_links_to_redis(article_links)
# save_articles_to_redis(article_links)
