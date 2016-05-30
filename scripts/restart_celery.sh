source /var/apps/news-discovery/env/bin/activate && cd /var/apps/news-discovery/news-discovery && supervisorctl stop all
sudo pkill -f worker
source /var/apps/news-discovery/env/bin/activate && cd /var/apps/news-discovery/news-discovery && echo yes | celery -A taskrunner purge && supervisorctl restart all