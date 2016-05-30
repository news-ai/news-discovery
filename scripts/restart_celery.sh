source /var/apps/news-discovery/env/bin/activate && cd /var/apps/news-discovery/news-discovery && supervisorctl stop all
sudo pkill -f worker
source /var/apps/news-discovery/env/bin/activate && cd /var/apps/news-discovery/news-discovery && echo yes | celery -A taskrunner purge && supervisorctl restart all
curl --retry 3 https://hchk.io/7c634fd9-ad47-40d6-a491-9284c58e2ec6
