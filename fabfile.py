from fabric.api import *

env.hosts = [
    '13.92.141.82'
]

env.user = "api"


def update_upgrade():
    """
        Update the default OS installation's
        basic default tools.
    """
    run("sudo apt update")
    run("sudo apt -y upgrade")


def update_server():
    update_upgrade()


def celery_purge():
    with cd("/var/apps/news-discovery"), prefix('source /var/apps/news-discovery/env/bin/activate'):
        with cd("/var/apps/news-discovery/news-discovery"):
            run('celery -A taskrunner purge')


def restart_discovery():
    with cd("/var/apps/news-discovery"), prefix('source /var/apps/news-discovery/env/bin/activate'):
        with cd("/var/apps/news-discovery/news-discovery"):
            run('git pull origin master')
            run('pip install -r requirements.txt')
            run('supervisorctl restart api workers:celeryd1 workers:celeryd2 workers:celeryd3')