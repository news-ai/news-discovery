# Stdlib imports
from __future__ import print_function
import os
import json

# Third-party app imports
import redis
import feedparser
import requests
from celery import chain
from pymongo import MongoClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Imports from app
from taskrunner import app
from discovery.internal import context

# Removing requests warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Setting up Redis & Mongo Instances
r = redis.StrictRedis()
client = MongoClient(connect=False)
db = client.news_discovery
seen_collection = db.discovered


# 15 min
# example: url = [RSS_LINK, ARTICLE_LINK_TAG, CAN_RUN, RSS_ID]
@app.task
def save_all_publisher_feeds_to_redis():
    token = context.get_login_token(False)
    feed_urls = []
    res = context.get_publisherfeeds(token).json()
    for publisher in res.get('results'):
        if len(publisher.get('tags')) > 0:
            feed_urls.append([publisher['feed_url'], publisher[
                             'tags'], True, publisher['id']])
        else:
            feed_urls.append(
                [publisher['feed_url'], None, True, publisher['id']])

    # add all non-feed url
    feed_urls.append(['http://www.nytimes.com', None, False, None])

    r.set('publisher_feeds', json.dumps(feed_urls))
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


def check_publisher_feeds():
    # updates the list of publisher feeds that we are checking
    if r.exists('publisher_feeds') is False:
        token = context.get_login_token(False)
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
def save_all_articles_to_redis():
    check_publisher_feeds()
    feeds = r.get('publisher_feeds')
    if feeds is None:
        return False
    feeds = json.loads(feeds)
    for feed in feeds:
        get_rss_from_publisher_feeds.delay(feed)
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
