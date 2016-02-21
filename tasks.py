from celery import Celery
BROKER_URL = 'redis://localhost:6379/0'

app = Celery('tasks', broker='amqp://guest@localhost//')


@app.task
def add(x, y):
    return x+y
