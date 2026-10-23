from flask_sqlalchemy import SQLAlchemy
from celery import Celery

db = SQLAlchemy()

def make_celery(app=None):
    celery = Celery(
        app.import_name if app else 'cortexgrid',
        broker=app.config['CELERY_BROKER_URL'] if app else 'redis://localhost:6379/0',
        backend=app.config['CELERY_RESULT_BACKEND'] if app else 'redis://localhost:6379/0'
    )
    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask
    return celery

celery_app = Celery('cortexgrid')
