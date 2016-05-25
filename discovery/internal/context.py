# Stdlib imports
from __future__ import print_function
import json
import os

# Third-party app imports
import requests
from urlparse import urlparse
from newspaper import Article
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Imports from app
from middleware import config
from discovery.utils.urls import url_validate

# Removing requests warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Setting up correct urls
base_url = config.BASE_URL
context_base_url = config.CONTEXT_BASE_URL


def get_login_token(from_discovery):
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "username": config.CONTEXT_API_USERNAME,
        "password": config.CONTEXT_API_PASSWORD,
    }

    context_url = base_url
    if from_discovery:
        context_url = context_base_url

    r = requests.post(context_url + "/jwt-token/",
                      headers=headers, data=json.dumps(payload), verify=False)
    data = json.loads(r.text)
    token = data.get('token')
    return token


def get_publisher(token):
    if token is None:
        print('Missing token')
        return

    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    r = requests.get(base_url + '/publisherfeeds/?limit=1000', headers=headers,
                     verify=False)
    return r


def post_to_news_processing(url):
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }

    payload = {
        "url": url
    }

    r = requests.get(config.NEWS_PROCESSING_URL + '/processing',
                     headers=headers, data=json.dumps(payload), verify=False)
