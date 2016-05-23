import json
import redis

r = redis.StrictRedis()
urls = json.loads(r.get('pending_urls'))
articles = []
for url in urls:
    article = json.loads(r.get(url))
    articles.append(article)

with open('batch_articles.json', 'w') as outfile:
    json.dump(articles, outfile)

with open('article_urls.json', 'w') as outfile:
    json.dump(urls, outfile)
