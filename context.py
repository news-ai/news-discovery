import requests
import json
import os
from urlparse import urlparse

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


def url_validate(url):
    url = urlparse(url)
    return (
        url.scheme + "://" + url.netloc +
        url.path, url.scheme + "://" + url.netloc
    )


def read_article(url, token):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    url, publisher = url_validate(url)

    data = {}
    data['url'] = url
    data['name'] = article.title  # Get Title
    if article.publish_date:
        data['created_at'] = str(article.publish_date)
    data['header_image'] = article.top_image
    data['basic_summary'] = article.summary
    data['authors'] = post_author(publisher, article.authors, token)

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

    payload = read_article(url, token)

    r = requests.post(base_url + '/articles/',
                      headers=headers, data=json.dumps(payload), verify=False)
    return r


def is_author_valid(author_name):
    if len(author_name.split(' ')) > 3:
        return False
    return True


def post_author(publisher, authors, token):
    if token is None:
        print 'Missing token'
        return

    if len(authors) is 0:
        return []

    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    author_list = []

    for author in authors:
        r = requests.get(base_url + '/authors/?name=' + author + '&writes_for__url=' + publisher,
                         headers=headers, verify=False)
        data = json.loads(r.text)
        if 'results' in data and len(data['results']) > 0:
            author_list.append(data['results'][0])
        else:
            r = requests.get(base_url + '/publishers/?url=' + publisher,
                             headers=headers, verify=False)
            data = json.loads(r.text)
            if 'results' in data and len(data['results']) is 1:
                payload = {
                    'name': author,
                    'publisher': data['results'][0],
                }
                if is_author_valid(author):
                    r = requests.post(base_url + '/authors/',
                                      headers=headers, data=json.dumps(payload), verify=False)
                    data = json.loads(r.text)
                    print data
                    author_list.append(data)

    return author_list


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

def get_publisher(token):
    if token is None:
        print 'Missing token'
        return
    
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    r = requests.get(base_url + '/publisherfeeds/?9', headers=headers,
            verify=False)
    return r

