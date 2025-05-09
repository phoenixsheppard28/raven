from celery import Celery
from openai import OpenAI
from internal.secrets import settings
from internal.db_setup import engine
from sqlmodel import Session, select
from internal.models import SourcePage, TargetPage
import uuid
from crawler.run_spider import run_spider


app = Celery('tasks', broker=settings.REDIS_URL) # redis is used as the broker 
chat_client=OpenAI(api_key=settings.OPENAI_API_KEY)


def scrape_and_store(url:str):
    try:
        task_id = uuid.uuid4() # this is the celery generated UUID we can use to index the task once completed 

        p = SourcePage(
                uid = task_id, # 
                url=url,
                status='PENDING') # set to pending when creating task 
        with Session(engine) as session:
            session.add(p)
            session.commit() # ? n+1 querry problem though, look into this
        
        target_keywords = ["Budget", "ACFR", "Finance Director", "CFO", "Financial Report", "Expenditure", "Revenue", "General Fund", "Capital Improvement Plan", "Fiscal Year", "Audit", "Auditor", "Treasurer", "Bond Issuance", "Municipal Bonds", "Debt Service", "Fund Balance", "Operating Budget", "Financial Statement", "Public Finance", "Controller", "Accounting", "CAFR", "GFOA", "Financial Planning", "Budget Hearing", "Budget Proposal", "Budget Adoption", "Reserve Fund", "Financial Forecast"]
        # will make adjustable in the future
  
        results = run_spider(url,target_keywords)

        with Session(engine) as session:
            source_page = session.exec(select(SourcePage).filter(SourcePage.uid==task_id)).first() # should only be one unless uuid collide 
            if not source_page:
                raise Exception
            source_page.status="COMPLETE"

            for result in results:
                item = TargetPage(
                    id= uuid.uuid4(),
                    job_uid=task_id,
                    target_url= result["url"],
                    file_type=result["file_type"],
                    relevance_score=result["relevance_score"],
                    matched_keywords=result["keywords"], # TODO must fix this one
                    text=result["text"] if result["text"] else None
                )
                session.add(item)

            session.commit()
            
        return {"status": "success", "result_count": len(results)}


    except Exception as e:
        with Session(engine) as session:
            source_page = session.exec(select(SourcePage).filter(SourcePage.uid == task_id)).first()
        if source_page:
            source_page.status = "FAILED"
            session.commit()


if __name__ == "__main__":
    url = "https://www.a2gov.org/"
    scrape_and_store(url)
    