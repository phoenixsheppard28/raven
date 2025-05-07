from celery import Celery
import time
from openai import OpenAI

app = Celery('tasks', broker='redis://localhost') # redis is used as the broker 

chat_client=OpenAI()

@app.task(bind=True) # bind allows accessing of self
def scrape_and_store(self,url:str):
    task_id = self.request.id # this is the celery generated UUID
    return task_id
   