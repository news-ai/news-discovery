from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'America/New York'
CELERYBEAT_SCHEDULE = {
        'every-thirty-minute-feed': {
            'task': 'feed.post_all_feeds',
            'schedule': crontab(minute=15),
            'args': ()
            },
        }
