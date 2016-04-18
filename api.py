# Stdlib imports
import json

# Third-party app imports
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from urlparse import urlparse

# Imports from app
import context

app = Flask(__name__)
CORS(app)

# if not config.DEBUG:
#     client = Client(
#         'https://99f7cb4fd29148f783ef5300f867570d:dabc526c069241dd852cc2b756c2cd06@app.getsentry.com/69539')


@app.route("/discovery", methods=['POST'])
def discovery_server():
    content = request.json
    stops = ['www', 'com', 'org', 'io']
    url = urlparse(content.get('url')).netloc
    name = [w for w in url.split('.')
            if w not in stops][0]
    short_name = name[0:5]
    is_approved = False
    token = context.get_login_token()
    pr = context.post_publisher(
            'http://' + url,
            name,
            short_name,
            is_approved,
            token)
    article = context.read_article_without_author(content.get('url'))
    article['authors'] = []
    article['added_by'] = 'https://context.newsai.org/api/users/' + \
        str(content.get('added_by')) + '/'
    articles = []
    articles.append(article)
    ar = context.post_article_without_author(articles, token)
    return jsonify({"details": ar.text})

if __name__ == '__main__':
    app.run(port=int('8000'))
