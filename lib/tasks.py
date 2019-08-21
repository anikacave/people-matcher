from celery import Celery

from lib import geo

app = Celery("lib.tasks", broker="redis://redis", backend="redis://redis")


@app.task
def add(x, y):
    return x + y


@app.task
def geocode(address):
    return geo.geocode(address)
