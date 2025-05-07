from celery import Celery
import time
from openai import OpenAI
from internal.secrets import settings



app = Celery('tasks', broker=settings.REDIS_URL) # redis is used as the broker 

chat_client=OpenAI(api_key=settings.OPENAI_API_KEY)

@app.task(bind=True) # bind allows accessing of self
def scrape_and_store(self,url:str):
    task_id = self.request.id # this is the celery generated UUID we can use to index the task once completed 



    return task_id
   