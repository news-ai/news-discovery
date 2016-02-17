import requests
import json
import os


def get_login_token():
    headers = {
        "content-type": "application/json",
        "accept": "application/json"
    }
    payload = {
        "username": os.environ.get("NEWSAI_CONTEXT_API_USERNAME"),
        "password": os.environ.get("NEWSAI_CONTEXT_API_PASSWORD"),
    }
    r = requests.post("https://context.newsai.org/api/jwt-token/",
                      headers=headers, data=json.dumps(payload), verify=False)
    data = json.loads(r.text)
    token = data.get('token')
    return token


def post_article(url, token):
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "authorization": "Bearer " + token
    }

    payload = {
        "url": url,
    }

    r = requests.post('https://context.newsai.org/api/articles/',
                      headers=headers, data=json.dumps(payload), verify=False)
    return r.text
