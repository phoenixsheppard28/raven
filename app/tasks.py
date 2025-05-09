from celery import Celery
from openai import OpenAI
from app.internal.secrets import settings
from app.internal.db_setup import engine
from sqlmodel import Session, select
from app.internal.models import SourcePage, TargetPage
import uuid
from app.crawler.run_spider import run_spider
import crochet

app = Celery('tasks') 
app.config_from_object('app.celeryconfig')

chat_client=OpenAI(api_key=settings.OPENAI_API_KEY)


@app.task(bind=True) # bind allows accessing of self
def scrape_and_store(self, url:str):
    try:
        task_id = uuid.UUID(self.request.id) # this is the celery generated UUID we can use to index the task once completed 

        p = SourcePage(
                uid = task_id, 
                url=url,
                status='PENDING') # set to pending when creating task 
        with Session(engine) as session:
            session.add(p)
            session.commit() 
        
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
                    matched_keywords=result["keywords"] # TODO must fix this one
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
        return {"status": "failed", "error": str(e)}


