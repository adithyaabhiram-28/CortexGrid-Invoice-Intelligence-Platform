from app import create_app
from app.extensions import make_celery

app = create_app()
celery_app = make_celery(app)

# Import tasks so they get registered with Celery worker
from app.tasks.invoice_tasks import process_invoice_task

if __name__ == '__main__':
    celery_app.start()
