from fastapi import FastAPI, Depends
from tasks import scrape_and_store
from celery.result import AsyncResult
from internal.db_setup import engine, Page
from sqlmodel import Session, select
import uuid




app = FastAPI()

@app.post("/url")
async def submit_scrape(request_url:str): # submit a url to be scraped 
    result : AsyncResult = scrape_and_store.delay(request_url)
    p = Page(uid = uuid.UUID(result.id), # 
             url=request_url,
             status='PENDING',
             result='testing')
    
    with Session(engine) as session:
        session.add(p)
        session.commit()
    return "url added to db"

@app.get("/pages")
def read_pages():
    with Session(engine) as session:
        pages = session.exec(select(Page)).all()
        return pages

