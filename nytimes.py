import os
import requests
import json
import context

newswire = 'http://api.nytimes.com/svc/news/v3/content/all/all.json?api-key=' + \
    os.environ.get('NYTIMES')
data = requests.get(newswire).json()

token = context.get_login_token()

if token is not None:
    for result in data['results']:
        if result.get('url') is not None:
            r = context.post_article(result.get('url'), token)
            print r
else:
    print token
