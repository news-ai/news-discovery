import os
import requests
import json

# newswire = 'http://api.nytimes.com/svc/news/v3/content/all/all.json?api-key=' + os.environ.get('NYTIMES')

# data = requests.get(newswire).json()

# with open('data.json', 'w') as f:
#     json.dump(data, f)

with open('data.json', 'r') as f:
    data = json.load(f)

    for result in data['results']:
        print result['title']
        print result['abstract']
        print result['url']
        print

