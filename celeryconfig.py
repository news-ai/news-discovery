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
        'post-feeds-to-api-every-fifteen-minutes': {
            'task': 'feeds_to_api.post_all_feeds',
            'schedule': timedelta(minutes=15),
            'args': ()
            },
        'save_publisher_feeds_to_redis_every_fifteen-minutes': {
            'task': 'feeds_to_api.save_all_publisher_feeds_to_redis',
            'schedule': timedelta(minutes=15),
            'args': ()
            },
        'save-feeds-to-redis-every-minute': {
            'task': 'feeds_to_redis.save_all_feeds_to_redis',
            'schedule': timedelta(minutes=1),
            'args': ()
            },
        'save-nytime-articles-every-fifteen-minutes': {
            'task': 'feeds_to_redis.run_nytimes',
            'schedule': timedelta(minutes=15),
            'args': ()
            }
        }
