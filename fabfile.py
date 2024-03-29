# Third-party app imports
from fabric.api import *

env.hosts = [
    '13.92.141.82'
]

env.user = 'api'


def update_upgrade():
    '''
        Update the default OS installation's
        basic default tools.
    '''
    run('sudo apt update')
    run('sudo apt -y upgrade')


def update_server():
    update_upgrade()


def get_logs():
    get('/var/apps/log', '%(path)s')


def celery_purge():
    with cd('/var/apps/news-discovery'), prefix('source /var/apps/news-discovery/env/bin/activate'):
        with cd('/var/apps/news-discovery/news-discovery'):
            run('echo yes | celery -A taskrunner purge && supervisorctl restart workers:celeryd1 workers:celeryd2')


def deploy():
    with cd('/var/apps/news-discovery'), prefix('source /var/apps/news-discovery/env/bin/activate'):
        with cd('/var/apps/news-discovery/news-discovery'):
            run('git pull origin v2')
            run('pip install -r requirements.txt')
            run('supervisorctl reread')
            run('supervisorctl update')
            run('supervisorctl restart workers:celeryd1 workers:celeryd2')
