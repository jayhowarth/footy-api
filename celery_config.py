from celery import Celery
import os
import pika

rabbit_url = ""
credit = pika.PlainCredentials(username='guest', password='guest')
url_hog = "amqp://guest@192.168.0.246:49156//"
url_local = "amqp://guest@localhost:5672//"


app = Celery('footy',
             broker=url_local,
             include=['task'])

#app = Celery('footy', broker='amqp://guest@localhost//')
# redis_url = os.getenv("REDIS_URL", "redis://192.168.0.246:49154")
# redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
# app = Celery(__name__, broker=redis_url, backend=redis_url)
