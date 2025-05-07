from celery import Celery
import time

app = Celery('tasks', broker='redis://localhost')

@app.task
def scrape_and_store(url:str):
    time.sleep(5)
    print("hello")