from fastapi import FastAPI, Depends
from app.tasks import scrape_and_store
from celery.result import AsyncResult
from app.internal.db_setup import engine, SourcePage, TargetPage
from sqlmodel import Session, select
from typing import List


def add_tasks(urls:List[str]) -> List[AsyncResult]: #
    """ add tasks to the queue and return the task ids 
        Since the tasks are added sequentially, the order of the task ids 
        will be the same as the order of the urls
    """
    results = []
    for url in urls:
        result : AsyncResult = scrape_and_store.delay(url)
        results.append(result)
    return results

           

app = FastAPI()

@app.post("/url")
async def submit_scrape(request_url:str)->str: # submit a url to be scraped 
    result : AsyncResult = scrape_and_store.delay(request_url) 
    # todo add check to make sure it has not been scraped before unless an override is set
    
    return result.id # todo should probably move this to use the add_rows function

@app.post("/url/batch")
async def submit_batch_scrape(urls: List[str])-> List[str]: # submit a batch of urls to be scraped
   results = add_tasks(urls)
   return [task.id for task in results] 



@app.get("/pages")
def read_pages():
    with Session(engine) as session:
        pages = session.exec(select(SourcePage)).all()
        return pages

@app.get("/results/{uuid}")
def get_scrape_result(uuid:str):
    return {"message":f"Result for job {uuid}"}

# TODO create endpoints to access based off keywords, file types, rankings, etc.