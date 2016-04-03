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
        'post-feeds-to-api-every-thirty-minutes': {
            'task': 'feeds_to_api.post_batch_articles',
            'schedule': timedelta(minutes=30),
            'args': (10, 0)
            },
        'save-publisher-feeds-to-redis-every-thirty-minutes': {
            'task': 'feeds_to_api.save_all_publisher_feeds_to_redis',
            'schedule': timedelta(minutes=30),
            'args': ()
            },
        'save-articles-to-redis-every-fifteen-minutes': {
            'task': 'feeds_to_redis.save_all_articles_to_redis',
            'schedule': timedelta(minutes=15),
            'args': ()
            },
        'save-nytime-articles-every-fifteen-minutes': {
            'task': 'feeds_to_redis.run_nytimes',
            'schedule': timedelta(minutes=15),
            'args': ()
            }
        }
