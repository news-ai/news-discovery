import requests
import json
import os

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


def post_article(url, token):
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
    }

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
