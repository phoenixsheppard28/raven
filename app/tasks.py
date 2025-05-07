from celery import Celery
from openai import OpenAI
from internal.secrets import settings
from internal.db_setup import engine
from sqlmodel import Session
from internal.models import SourcePage, TargetPage
from scrapy import Selector
import uuid



app = Celery('tasks', broker=settings.REDIS_URL) # redis is used as the broker 
chat_client=OpenAI(api_key=settings.OPENAI_API_KEY)


@app.task(bind=True) # bind allows accessing of self
def scrape_and_store(self,url:str):
    task_id = self.request.id # this is the celery generated UUID we can use to index the task once completed 

    p = SourcePage(uid = uuid.UUID(task_id), # 
             url=url,
             status='PENDING',
             result='testing')
    with Session(engine) as session:
        session.add(p)
        session.commit() # ? n+1 querry problem though, look into this
    



    return task_id
   