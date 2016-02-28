from celery import Celery
def make_celery(app):
    celery = Celery(
        'taskrunner',
        broker='redis://localhost:6379/0',
        include=['feeds_to_api', 'feeds_to_redis'],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
