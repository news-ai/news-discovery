import requests
import json
import os

from newspaper import Article


base_url = 'https://context.newsai.org/api'


def get_login_token():
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "username": os.environ.get("NEWSAI_CONTEXT_API_USERNAME"),
        "password": os.environ.get("NEWSAI_CONTEXT_API_PASSWORD"),
    }
    r = requests.post(base_url + "/jwt-token/",
                      headers=headers, data=json.dumps(payload), verify=False)
    data = json.loads(r.text)
    token = data.get('token')
    return token


def entity_extraction(keywords, text):
    return []


def read_article(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    data = {}
    data['url'] = url
    data['name'] = article.title  # Get Title
    data['created_at'] = str(article.publish_date)
    data['header_image'] = article.top_image
    data['basic_summary'] = article.summary

    # data['keywords'] = article.keywords
    # entity_extraction(article.keywords, article.text)
    return data


def post_article(url, token):
    if token is None:
        print 'Missing token'
        return
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    payload = read_article(url)

    r = requests.post(base_url + '/articles/',
                      headers=headers, data=json.dumps(payload), verify=False)
    return r


def post_publisher(url, publisher, name, token):
    if token is None:
        print 'Missing token'
        return
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    payload = {
        "url": url,
        'publisher': publisher,
        'name': name
    }

    r = requests.post(base_url + '/publishers/',
                      headers=headers, data=json.dumps(payload), verify=False)
    return r
