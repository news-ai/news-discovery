import os
import requests
import redis
from taskrunner import app
import json
import context

r = redis.StrictRedis()
# if token is not None:
#     for result in data['results']:
#         if result.get('url') is not None:
#             r = context.post_article(result.get('url'), token)
#             print r
# else:
#     print token


def save_nytimes_to_redis():
    newswire = 'http://api.nytimes.com/svc/news/v3/content/all/all.json?api-key=' + \
        os.environ.get('NYTIMES')
    data = requests.get(newswire).json()
    for result in data['results']:
        if result.get('url') is not None:
            print result.get('url')
    # token = context.get_login_token()

save_nytimes_to_redis()
