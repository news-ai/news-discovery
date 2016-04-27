# Stdlib imports
import json

# Third-party app imports
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from raven.contrib.flask import Sentry
from urlparse import urlparse

# Imports from app
import context

app = Flask(__name__)
CORS(app)

sentry = Sentry(
    app, dsn='https://a1470015603f469faf398e861a887f0d:37fa444462f142008ba58e488679c9b4@app.getsentry.com/76018')


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
    article['added_by'] = 'https://internal.newsai.org/api/users/' + \
        str(content.get('added_by')) + '/'
    articles = []
    articles.append(article)
    ar = context.post_article_without_author(articles, token)
    return jsonify({"details": ar.text})

if __name__ == '__main__':
    app.run(port=int('8000'))
