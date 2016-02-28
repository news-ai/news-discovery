# news-discovery

Discovering and finding new news articles

Run Celery with:
`celery worker -A taskrunner --beat -l info -c 5`

Start Redis:
`redis-server`

Check if it's running:
`redis-cli ping`

####Notes:
Run `feeds_to_api.save_publisher_feeds_to_redis` first if starting with a new Redis
