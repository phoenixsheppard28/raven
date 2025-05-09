from fastapi import FastAPI, Depends
from app.tasks import scrape_and_store
from celery.result import AsyncResult
from app.internal.db_setup import engine, SourcePage, TargetPage
from sqlmodel import Session, select,delete
from typing import List, Optional


def add_tasks(urls:List[str],target_keywords:List[str]) -> List[AsyncResult]: #
    """
    Add scraping tasks to the Celery queue and return task IDs.

    Args:
        urls (List[str]): List of URLs to scrape.
        target_keywords (Optional[List[str]]): Optional list of keywords to prioritize during scraping.

    Returns:
        List[AsyncResult]: List of task results corresponding to the scraping jobs.
    """
    results = []
    for url in urls:
        result : AsyncResult = scrape_and_store.delay(url,target_keywords)
        results.append(result)
    return results

           

app = FastAPI()

@app.post("/scrape-url")
async def submit_scrape(request_url:str,target_keywords: Optional[List[str]])->str: # submit a url to be scraped 
    """
    Submit a single URL to be scraped.
    Args:
        request_url (str): The URL to scrape.
        target_keywords (Optional[List[str]]): Optional list of keywords to prioritize (e.g., "Budget", "ACFR").
    Returns:
        str: Task ID of the Celery scraping job.
    """
    result : AsyncResult = scrape_and_store.delay(request_url,target_keywords) 
    return result.id 

@app.post("/scrape-urls")
async def submit_batch_scrape(urls: List[str],target_keywords: Optional[List[str]])-> List[str]:
   """
    Submit a batch of URLs to be scraped in parallel.

    Args:
        urls (List[str]): List of URLs to scrape.
        target_keywords (Optional[List[str]]): Optional list of keywords to prioritize during scraping.

    Returns:
        List[str]: List of task IDs for each scraping job.
    """
   results = add_tasks(urls,target_keywords)
   return [task.id for task in results] 



@app.get("/pages")
def read_pages():
    """
    Retrieve all scraped source pages stored in the database.

    Returns:
        List[SourcePage]: List of stored source page entries.
    """
    with Session(engine) as session:
        pages = session.exec(select(SourcePage)).all()
        return pages

@app.get("/results/{uuid}")
def get_scrape_result(uuid:str):
    """
    Fetch the status or result of a scraping task by its task ID.

    Args:
        uuid (str): Task ID for the scraping job.

    Returns:
        dict: Placeholder message for now; should be expanded to return actual results.
    """
    return {"message":f"Result for job {uuid}"}

# TODO create endpoints to access based off keywords, file types, rankings, etc.

@app.delete("/reset-database")
def reset_db():
    """
    Reset the database by deleting all entries in SourcePage and TargetPage tables.
    This is useful for clearing out old data and starting fresh.
    Returns:
        dict: Confirmation message upon successful reset.
    """
    with Session(engine) as session:
        session.exec(delete(SourcePage))
        session.exec(delete(TargetPage))
        session.commit()
    return {"message": "Database reset successfully."}