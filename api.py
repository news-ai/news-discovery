# Stdlib imports
import json
import logging

# Third-party app imports
from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from flask_restful import Resource, Api, reqparse
from raven.contrib.flask import Sentry
from urlparse import urlparse

# Imports from app
import context

# Setting up Flask and API
app = Flask(__name__)
api = Api(app)
CORS(app)

# Setting up Sentry
sentry = Sentry(
    app, dsn='https://a1470015603f469faf398e861a887f0d:37fa444462f142008ba58e488679c9b4@app.getsentry.com/76018')

# Setting up parser
parser = reqparse.RequestParser()
parser.add_argument('url')
parser.add_argument('added_by')


class Discovery(Resource):

    def post(self):
        args = parser.parse_args()
        stops = ['www', 'com', 'org', 'io']
        url = urlparse(args['url']).netloc
        name = [w for w in url.split('.')
                if w not in stops][0]
        short_name = name[0:5]
        is_approved = False
        token = context.get_login_token(True)
        pr = context.post_publisher(
            'http://' + url,
            name,
            short_name,
            is_approved,
            token,
            True)
        article = context.read_article_without_author(args['url'])
        article['authors'] = []
        article['added_by'] = 'https://context.newsai.org/api/users/' + \
            str(args['added_by']) + '/'
        articles = []
        articles.append(article)
        ar = context.post_article_without_author(articles, token, True)
        return ar.json()

api.add_resource(Discovery, '/discovery')

if __name__ == '__main__':
    app.run(port=int('8000'), debug=True)
