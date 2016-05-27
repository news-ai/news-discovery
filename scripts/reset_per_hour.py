# Stdlib imports
from subprocess import call

# Third-party app imports
from apscheduler.schedulers.blocking import BlockingScheduler


def some_job():
    print call(["bash", "/home/api/restart_celery.sh"])

scheduler = BlockingScheduler()
scheduler.add_job(some_job, 'interval', hours=1)
scheduler.start()
