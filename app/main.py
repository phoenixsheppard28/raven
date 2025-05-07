from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import sqlite3
from tasks import scrape_and_store
from celery.result import AsyncResult



load_dotenv()


app = FastAPI()

@app.post("/submit-url")
async def submit_scrape(request:str):
    result : AsyncResult = scrape_and_store.delay(request)
    print(result.status)

