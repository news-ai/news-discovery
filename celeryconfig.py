# from celery.schedules import crontab
from datetime import timedelta

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {
    'post-feeds-to-news-processing-every-thirty-minutes': {
        'task': 'discovery.feeds_to_news_processing.post_articles_for_each_feed',
        'schedule': timedelta(minutes=30),
        'args': ()
    },
    'save-publisher-feeds-to-redis-every-thirty-minutes': {
        'task': 'discovery.feeds_to_redis.save_all_publisher_feeds_to_redis',
        'schedule': timedelta(minutes=30),
        'args': ()
    },
    'save-articles-to-redis-every-fifteen-minutes': {
        'task': 'discovery.feeds_to_redis.save_all_articles_to_redis',
        'schedule': timedelta(minutes=15),
        'args': ()
    },
    'save-nytime-articles-every-fifteen-minutes': {
        'task': 'discovery.feeds_to_redis.get_nytimes_links',
        'schedule': timedelta(minutes=15),
        'args': ()
    },
}
