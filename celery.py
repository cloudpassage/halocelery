import apputils
from celery import Celery
import os

app = Celery(backend=os.getenv("CELERY_BACKEND_URL"),
             broker=os.getenv("CELERY_BROKER_URL"),
             include=["halocelery.tasks"])

if __name__ == '__main__':
    app.start()
